#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:24

import numpy as np
from typing import List, Dict


class PerformanceAnalyzer:
    def __init__(self):
        self.min_data_threshold = 100
        self.min_sigma_threshold = 30
        self.min_interval_threshold = 100

    def calculate_performance_metrics(self, data: List[float]) -> Dict[str, float]:
        """计算性能指标 - 根据数据量决定计算内容"""
        if not data:
            return {'count': 0, 'insufficient_data': True}

        metrics = {}
        data_count = len(data)

        # 基础统计 - 总是计算
        metrics['count'] = data_count
        metrics['mean'] = np.mean(data)
        metrics['median'] = np.median(data)
        metrics['min'] = np.min(data)
        metrics['max'] = np.max(data)

        # 数据量检查
        if data_count < 5:
            metrics['insufficient_data'] = True
            metrics['data_status'] = '严重不足 (<5)'
            return metrics
        elif data_count < 10:
            metrics['insufficient_data'] = True
            metrics['data_status'] = '不足 (5-9)'
            return metrics

        # 基础扩展统计 (数据量 >= 10)
        metrics['std'] = np.std(data)
        metrics['variance'] = np.var(data)

        # 百分位数计算 - 根据数据量调整
        if data_count >= 50:
            percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        elif data_count >= 20:
            percentiles = [5, 25, 50, 75, 95]
        else:  # data_count >= 10
            percentiles = [5, 50, 95]

        for p in percentiles:
            metrics[f'p{p}'] = np.percentile(data, p)

        # 西格玛水平计算 (数据量 >= 30)
        if data_count >= self.min_sigma_threshold:
            sigma_metrics = self._calculate_sigma_levels(data, metrics['mean'], metrics['std'])
            metrics.update(sigma_metrics)
        else:
            metrics['sigma_status'] = f'数据量不足 ({data_count} < {self.min_sigma_threshold})'

        # 综合区间分析 (数据量 >= 100)
        if data_count >= self.min_interval_threshold:
            interval_metrics = self._calculate_comprehensive_interval(data, metrics)
            metrics.update(interval_metrics)
        else:
            metrics['interval_status'] = f'数据量不足 ({data_count} < {self.min_interval_threshold})'

        # 数据质量评估
        metrics.update(self._assess_data_quality(data_count))

        return metrics

    def _calculate_sigma_levels(self, data: List[float], mean: float, std: float) -> Dict[str, float]:
        """计算西格玛水平 - 包括2sigma、3sigma和6sigma"""
        sigma_levels = {}

        if std == 0:
            return {
                'sigma_2_lower': mean,
                'sigma_2_upper': mean,
                'sigma_3_lower': mean,
                'sigma_3_upper': mean,
                'sigma_6_lower': mean,
                'sigma_6_upper': mean,
                'within_2sigma': 100.0,
                'within_3sigma': 100.0,
                'within_6sigma': 100.0,
            }

        # 2西格玛范围 (95.45%)
        sigma_2_lower = mean - 2 * std
        sigma_2_upper = mean + 2 * std

        # 3西格玛范围 (99.73%)
        sigma_3_lower = mean - 3 * std
        sigma_3_upper = mean + 3 * std

        # 6西格玛范围 (99.99966%)
        sigma_6_lower = mean - 6 * std
        sigma_6_upper = mean + 6 * std

        # 计算实际落在范围内的数据比例
        within_2sigma = sum(1 for x in data if sigma_2_lower <= x <= sigma_2_upper) / len(data) * 100
        within_3sigma = sum(1 for x in data if sigma_3_lower <= x <= sigma_3_upper) / len(data) * 100
        within_6sigma = sum(1 for x in data if sigma_6_lower <= x <= sigma_6_upper) / len(data) * 100

        sigma_levels.update({
            'sigma_2_lower': sigma_2_lower,
            'sigma_2_upper': sigma_2_upper,
            'sigma_3_lower': sigma_3_lower,
            'sigma_3_upper': sigma_3_upper,
            'sigma_6_lower': sigma_6_lower,
            'sigma_6_upper': sigma_6_upper,
            'within_2sigma': within_2sigma,
            'within_3sigma': within_3sigma,
            'within_6sigma': within_6sigma
        })

        return sigma_levels

    def _calculate_comprehensive_interval(self, data: List[float], metrics: Dict[str, float]) -> Dict[str, float]:
        """计算综合区间 - 结合Sigma和百分位数"""
        interval_metrics = {}

        # 基于数据分布特征的综合区间
        mean = metrics['mean']
        std = metrics['std']
        p1 = metrics.get('p1', np.percentile(data, 1))
        p5 = metrics.get('p5', np.percentile(data, 5))
        p95 = metrics.get('p95', np.percentile(data, 95))
        p99 = metrics.get('p99', np.percentile(data, 99))

        # 方法1: 基于西格玛的区间
        sigma_2_lower = max(mean - 2 * std, np.min(data))
        sigma_2_upper = min(mean + 2 * std, np.max(data))
        sigma_3_lower = max(mean - 3 * std, np.min(data))
        sigma_3_upper = min(mean + 3 * std, np.max(data))

        # 方法2: 基于百分位数的区间
        percentile_based_lower = p5
        percentile_based_upper = p95
        strict_percentile_lower = p1
        strict_percentile_upper = p99

        # 推荐的综合区间 - 结合两种方法
        if metrics.get('within_3sigma', 0) > 99:
            # 数据分布接近正态，使用2sigma区间
            recommended_lower = sigma_2_lower
            recommended_upper = sigma_2_upper
            interval_method = "2 Sigma区间 (数据分布接近正态)"
        else:
            # 数据分布有偏，使用百分位区间
            recommended_lower = percentile_based_lower
            recommended_upper = percentile_based_upper
            interval_method = "百分位区间 (P5-P95)"

        # 严格区间 (6sigma或P1-P99)
        if metrics.get('within_6sigma', 0) > 99.9:
            strict_lower = metrics.get('sigma_6_lower', sigma_3_lower)
            strict_upper = metrics.get('sigma_6_upper', sigma_3_upper)
            strict_method = "6 Sigma区间 (极高数据质量)"
        else:
            strict_lower = strict_percentile_lower
            strict_upper = strict_percentile_upper
            strict_method = "严格百分位区间 (P1-P99)"

        # 确保区间在数据范围内
        recommended_lower = max(recommended_lower, np.min(data))
        recommended_upper = min(recommended_upper, np.max(data))
        strict_lower = max(strict_lower, np.min(data))
        strict_upper = min(strict_upper, np.max(data))

        # 计算在推荐区间内的数据比例
        within_recommended = sum(1 for x in data if recommended_lower <= x <= recommended_upper) / len(data) * 100
        within_strict = sum(1 for x in data if strict_lower <= x <= strict_upper) / len(data) * 100

        interval_metrics.update({
            'sigma_2_lower': sigma_2_lower,
            'sigma_2_upper': sigma_2_upper,
            'sigma_3_lower': sigma_3_lower,
            'sigma_3_upper': sigma_3_upper,
            'sigma_6_lower': metrics.get('sigma_6_lower', sigma_3_lower),
            'sigma_6_upper': metrics.get('sigma_6_upper', sigma_3_upper),
            'percentile_based_lower': percentile_based_lower,
            'percentile_based_upper': percentile_based_upper,
            'strict_percentile_lower': strict_percentile_lower,
            'strict_percentile_upper': strict_percentile_upper,
            'recommended_lower': recommended_lower,
            'recommended_upper': recommended_upper,
            'strict_lower': strict_lower,
            'strict_upper': strict_upper,
            'within_recommended': within_recommended,
            'within_strict': within_strict,
            'interval_method': interval_method,
            'strict_method': strict_method
        })

        return interval_metrics

    def _assess_data_quality(self, data_count: int) -> Dict[str, str]:
        """评估数据质量"""
        quality_metrics = {}

        if data_count >= 1000:
            quality_metrics['data_quality'] = '优秀'
        elif data_count >= 500:
            quality_metrics['data_quality'] = '良好'
        elif data_count >= 100:
            quality_metrics['data_quality'] = '一般'
        elif data_count >= 30:
            quality_metrics['data_quality'] = '不足'
        else:
            quality_metrics['data_quality'] = '严重不足'

        return quality_metrics

    def generate_analysis_report(self, metrics: Dict[str, float], filename: str = "数据") -> str:
        """生成分析报告 - 专注于单个文件的详细分析"""
        result = "=" * 60 + "\n"
        result += f"           {filename} 性能分析报告\n"
        result += "=" * 60 + "\n"

        # 数据质量状态
        data_count = metrics['count']
        data_quality = metrics.get('data_quality', '未知')
        data_status = metrics.get('data_status', '')

        result += f"样本数量: {data_count:.0f}  {data_quality}"
        if data_status:
            result += f" ({data_status})"
        result += "\n\n"

        # 数据量严重不足的情况
        if metrics.get('insufficient_data', False) and data_count < 10:
            result += "数据量严重不足警告:\n"
            result += "-" * 40 + "\n"
            result += "  当前数据量无法进行有效的统计分析\n"
            result += "  建议收集更多数据以获得可靠分析结果\n\n"

            result += "基础统计 (仅供参考):\n"
            result += "-" * 40 + "\n"
            result += f"  平均值: {metrics['mean']:.2f}\n"
            result += f"  中位数: {metrics['median']:.2f}\n"
            result += f"  最小值: {metrics['min']:.2f}\n"
            result += f"  最大值: {metrics['max']:.2f}\n\n"
            return result

        # 数据量提示
        if metrics.get('insufficient_data', False):
            result += "数据量较少，部分分析受限\n\n"

        result += "基础统计:\n"
        result += "-" * 40 + "\n"
        result += f"  平均值 (Mean): {metrics['mean']:.2f}\n"
        result += f"  中位数 (Median): {metrics['median']:.2f}\n"
        result += f"  最小值: {metrics['min']:.2f}\n"
        result += f"  最大值: {metrics['max']:.2f}\n"

        if 'std' in metrics:
            result += f"  标准差 (Std): {metrics['std']:.2f}\n"
            result += f"  方差: {metrics['variance']:.2f}\n\n"

            result += "百分位数:\n"
            result += "-" * 40 + "\n"
            if 'p1' in metrics:
                result += f"  P1: {metrics['p1']:.2f}\n"
            if 'p5' in metrics:
                result += f"  P5: {metrics['p5']:.2f}\n"
            if 'p10' in metrics:
                result += f"  P10: {metrics['p10']:.2f}\n"
            if 'p25' in metrics:
                result += f"  P25: {metrics['p25']:.2f}\n"
            result += f"  P50: {metrics['p50']:.2f}\n"
            if 'p75' in metrics:
                result += f"  P75: {metrics['p75']:.2f}\n"
            if 'p90' in metrics:
                result += f"  P90: {metrics['p90']:.2f}\n"
            result += f"  P95: {metrics['p95']:.2f}\n"
            if 'p99' in metrics:
                result += f"  P99: {metrics['p99']:.2f}\n\n"

            # 西格玛分析
            if 'sigma_3_lower' in metrics:
                result += self._generate_sigma_analysis(metrics)
            elif 'sigma_status' in metrics:
                result += "西格玛分析:\n"
                result += "-" * 40 + "\n"
                result += f"  {metrics['sigma_status']}，无法进行西格玛分析\n\n"

            # 综合区间分析
            if 'recommended_lower' in metrics:
                result += self._generate_interval_analysis(metrics)
            elif 'interval_status' in metrics:
                result += "区间分析:\n"
                result += "-" * 40 + "\n"
                result += f"  {metrics['interval_status']}，无法进行综合区间分析\n\n"
        else:
            result += "\n"
            result += "数据量不足，无法计算标准差和百分位数\n"
            result += "建议收集更多数据点以获得完整分析\n\n"

        # 数据收集建议
        result += self._generate_data_collection_advice(data_count)

        return result

    def _generate_sigma_analysis(self, metrics: Dict[str, float]) -> str:
        """生成西格玛分析报告"""
        result = "西格玛范围分析:\n"
        result += "-" * 40 + "\n"

        # 使用安全的get方法，避免KeyError
        sigma_2_lower = metrics.get('sigma_2_lower')
        sigma_2_upper = metrics.get('sigma_2_upper')
        sigma_3_lower = metrics.get('sigma_3_lower')
        sigma_3_upper = metrics.get('sigma_3_upper')
        sigma_6_lower = metrics.get('sigma_6_lower')
        sigma_6_upper = metrics.get('sigma_6_upper')

        if sigma_2_lower is not None and sigma_2_upper is not None:
            result += f"  2σ范围: [{sigma_2_lower:.2f}, {sigma_2_upper:.2f}]\n"
            result += f"  数据在2σ范围内: {metrics.get('within_2sigma', 0):.2f}%\n"

        if sigma_3_lower is not None and sigma_3_upper is not None:
            result += f"  3σ范围: [{sigma_3_lower:.2f}, {sigma_3_upper:.2f}]\n"
            result += f"  数据在3σ范围内: {metrics.get('within_3sigma', 0):.2f}%\n"

        # 6sigma分析
        if sigma_6_lower is not None and sigma_6_upper is not None:
            result += f"  6σ范围: [{sigma_6_lower:.2f}, {sigma_6_upper:.2f}]\n"
            result += f"  数据在6σ范围内: {metrics.get('within_6sigma', 0):.2f}%\n\n"
        else:
            result += "\n"

        return result

    def _generate_interval_analysis(self, metrics: Dict[str, float]) -> str:
        """生成综合区间分析报告"""
        result = "综合区间分析:\n"
        result += "-" * 40 + "\n"
        result += f"  推荐区间: [{metrics.get('recommended_lower', 0):.2f}, {metrics.get('recommended_upper', 0):.2f}]\n"
        result += f"  区间内数据比例: {metrics.get('within_recommended', 0):.2f}%\n"
        result += f"  区间选择方法: {metrics.get('interval_method', 'N/A')}\n\n"

        result += "严格区间分析:\n"
        result += "-" * 40 + "\n"
        result += f"  严格区间: [{metrics.get('strict_lower', 0):.2f}, {metrics.get('strict_upper', 0):.2f}]\n"
        result += f"  区间内数据比例: {metrics.get('within_strict', 0):.2f}%\n"
        result += f"  区间选择方法: {metrics.get('strict_method', 'N/A')}\n\n"

        # 区间选择建议
        result += "区间选择建议:\n"
        result += "-" * 40 + "\n"
        within_recommended = metrics.get('within_recommended', 0)
        if within_recommended > 90:
            result += "  [OK] 推荐区间覆盖了大部分数据，适合作为默认参考\n"
        else:
            result += "  [警告] 推荐区间覆盖数据较少，建议使用严格区间\n"

        within_3sigma = metrics.get('within_3sigma', 0)
        if within_3sigma > 95:
            result += "  [OK] 数据分布接近正态，Sigma区间是合理选择\n"
        else:
            result += "  [信息] 数据分布有偏，建议使用百分位区间\n"

        within_6sigma = metrics.get('within_6sigma', 0)
        if within_6sigma > 99.9:
            result += "  [优秀] 数据质量极高，6Sigma区间可作为严格标准\n"

        result += "\n"

        return result

    def _generate_data_collection_advice(self, data_count: int) -> str:
        """生成数据收集建议"""
        result = "数据收集建议:\n"
        result += "-" * 40 + "\n"

        if data_count < 10:
            result += "  [警报] 立即停止分析，数据量严重不足\n"
            result += "  → 建议收集至少10个数据点\n"
        elif data_count < 30:
            result += "  [警告] 数据量不足，只能进行基础分析\n"
            result += "  → 建议收集至少30个数据点进行西格玛分析\n"
        elif data_count < 100:
            result += "  [信息] 数据量一般，可进行西格玛分析\n"
            result += "  → 建议收集至少100个数据点进行综合区间分析\n"
        elif data_count < 500:
            result += "  [OK] 数据量足够进行完整分析\n"
            result += "  → 当前数据质量良好\n"
        else:
            result += "  [优秀] 数据量充足，分析结果可靠\n"
            result += "  → 当前数据质量优秀\n"

        result += "\n"
        return result
