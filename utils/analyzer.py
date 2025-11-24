#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:24

import numpy as np
from typing import List, Dict


class PerformanceAnalyzer:
    def __init__(self):
        self.min_data_threshold = 500  # 最小数据量要求

    def calculate_performance_metrics(self, data: List[float]) -> Dict[str, float]:
        """计算性能指标 - 根据数据量决定计算内容"""
        if not data:
            return {}

        metrics = {}
        data_count = len(data)

        # 基础统计
        metrics['count'] = data_count
        metrics['mean'] = np.mean(data)
        metrics['median'] = np.median(data)  # 总是计算中位数

        # 根据数据量决定计算内容
        if data_count >= self.min_data_threshold:
            # 数据量足够，计算完整统计
            metrics['std'] = np.std(data)

            # 百分位数
            percentiles = [5, 50, 90, 95, 99]
            for p in percentiles:
                metrics[f'p{p}'] = np.percentile(data, p)

            # 西格玛水平计算
            metrics.update(self._calculate_sigma_levels(data, metrics['mean'], metrics['std']))

            # 综合区间分析
            metrics.update(self._calculate_comprehensive_interval(data, metrics))
        else:
            # 数据量不足
            metrics['insufficient_data'] = True

        return metrics

    def _calculate_sigma_levels(self, data: List[float], mean: float, std: float) -> Dict[str, float]:
        """计算西格玛水平"""
        sigma_levels = {}

        if std == 0:
            # 标准差为0，所有数据相同
            return {
                'sigma_3_lower': mean,
                'sigma_3_upper': mean,
                'sigma_6_lower': mean,
                'sigma_6_upper': mean,
                'within_3sigma': 100.0,
                'within_6sigma': 100.0
            }

        # 3西格玛范围 (99.73% 的数据应该落在这个范围内)
        sigma_3_lower = mean - 3 * std
        sigma_3_upper = mean + 3 * std

        # 6西格玛范围 (99.99966% 的数据应该落在这个范围内)
        sigma_6_lower = mean - 6 * std
        sigma_6_upper = mean + 6 * std

        # 计算实际落在范围内的数据比例
        within_3sigma = sum(1 for x in data if sigma_3_lower <= x <= sigma_3_upper) / len(data) * 100
        within_6sigma = sum(1 for x in data if sigma_6_lower <= x <= sigma_6_upper) / len(data) * 100

        sigma_levels.update({
            'sigma_3_lower': sigma_3_lower,
            'sigma_3_upper': sigma_3_upper,
            'sigma_6_lower': sigma_6_lower,
            'sigma_6_upper': sigma_6_upper,
            'within_3sigma': within_3sigma,
            'within_6sigma': within_6sigma
        })

        return sigma_levels

    def _calculate_comprehensive_interval(self, data: List[float], metrics: Dict[str, float]) -> Dict[str, float]:
        """计算综合区间 - 结合3 Sigma和6 Sigma"""
        interval_metrics = {}

        # 基于数据分布特征的综合区间
        mean = metrics['mean']
        std = metrics['std']
        p95 = metrics['p95']
        p99 = metrics['p99']

        # 方法1: 基于西格玛的区间
        sigma_based_lower = max(mean - 4 * std, np.min(data))  # 使用4西格玛作为下限
        sigma_based_upper = min(mean + 4 * std, np.max(data))  # 使用4西格玛作为上限

        # 方法2: 基于百分位数的区间
        percentile_based_lower = metrics['p5']
        percentile_based_upper = p99

        # 方法3: 稳健区间 (结合均值和百分位数)
        robust_lower = max(mean - 2 * std, percentile_based_lower)
        robust_upper = min(mean + 2 * std, percentile_based_upper)

        # 推荐的综合区间
        # 结合3sigma和实际数据分布，取一个平衡点
        if metrics['within_3sigma'] > 99:
            # 数据分布接近正态，使用3sigma区间
            recommended_lower = metrics['sigma_3_lower']
            recommended_upper = metrics['sigma_3_upper']
            interval_method = "3 Sigma区间 (数据分布接近正态)"
        else:
            # 数据分布有偏，使用稳健区间
            recommended_lower = robust_lower
            recommended_upper = robust_upper
            interval_method = "稳健区间 (结合2 Sigma和P99)"

        # 确保区间在数据范围内
        recommended_lower = max(recommended_lower, np.min(data))
        recommended_upper = min(recommended_upper, np.max(data))

        # 计算在推荐区间内的数据比例
        within_recommended = sum(1 for x in data if recommended_lower <= x <= recommended_upper) / len(data) * 100

        interval_metrics.update({
            'sigma_based_lower': sigma_based_lower,
            'sigma_based_upper': sigma_based_upper,
            'percentile_based_lower': percentile_based_lower,
            'percentile_based_upper': percentile_based_upper,
            'robust_lower': robust_lower,
            'robust_upper': robust_upper,
            'recommended_lower': recommended_lower,
            'recommended_upper': recommended_upper,
            'within_recommended': within_recommended,
            'interval_method': interval_method
        })

        return interval_metrics

    def generate_analysis_report(self, metrics: Dict[str, float]) -> str:
        """生成分析报告"""
        result = "=" * 50 + "\n"
        result += "性能分析报告\n"
        result += "=" * 50 + "\n"
        result += f"样本数量: {metrics['count']:.0f}\n"

        # 数据量提示
        if metrics['count'] < self.min_data_threshold:
            result += f"⚠ 数据量较少 (<{self.min_data_threshold})，仅提供基础分析\n\n"

        result += "基础统计:\n"
        result += f"  平均值 (Mean): {metrics['mean']:.2f}\n"
        result += f"  中位数 (Median): {metrics['median']:.2f}\n"

        if 'std' in metrics:
            result += f"  标准差 (Std):  {metrics['std']:.2f}\n\n"

            result += "百分位数:\n"
            result += f"  P5: {metrics['p5']:.2f}\n"
            result += f"  P50: {metrics['p50']:.2f}\n"
            result += f"  P90: {metrics['p90']:.2f}\n"
            result += f"  P95: {metrics['p95']:.2f}\n"
            result += f"  P99: {metrics['p99']:.2f}\n\n"

            # 西格玛分析
            result += self._generate_sigma_analysis(metrics)

            # 综合区间分析
            result += self._generate_interval_analysis(metrics)
        else:
            result += "\n"
            result += "数据量不足，无法计算标准差和百分位数\n"
            result += f"建议收集至少 {self.min_data_threshold} 个数据点以获得完整分析\n\n"

        return result

    def _generate_sigma_analysis(self, metrics: Dict[str, float]) -> str:
        """生成西格玛分析报告"""
        result = "西格玛范围:\n"
        result += f"  3σ范围: [{metrics['sigma_3_lower']:.2f}, {metrics['sigma_3_upper']:.2f}]\n"
        result += f"  数据在3σ范围内: {metrics['within_3sigma']:.2f}%\n"
        result += f"  6σ范围: [{metrics['sigma_6_lower']:.2f}, {metrics['sigma_6_upper']:.2f}]\n"
        result += f"  数据在6σ范围内: {metrics['within_6sigma']:.2f}%\n\n"

        return result

    def _generate_interval_analysis(self, metrics: Dict[str, float]) -> str:
        """生成综合区间分析报告"""
        result = "综合区间分析:\n"
        result += f"  推荐区间: [{metrics['recommended_lower']:.2f}, {metrics['recommended_upper']:.2f}]\n"
        result += f"  区间内数据比例: {metrics['within_recommended']:.2f}%\n"
        result += f"  区间选择方法: {metrics['interval_method']}\n\n"

        result += "其他区间参考:\n"
        result += f"  4σ区间: [{metrics['sigma_based_lower']:.2f}, {metrics['sigma_based_upper']:.2f}]\n"
        result += f"  百分位区间(P5-P99): [{metrics['percentile_based_lower']:.2f}, {metrics['percentile_based_upper']:.2f}]\n"
        result += f"  稳健区间: [{metrics['robust_lower']:.2f}, {metrics['robust_upper']:.2f}]\n\n"

        # 区间选择建议
        result += "区间选择建议:\n"
        if metrics['within_recommended'] > 95:
            result += "  ✅ 推荐区间覆盖了大部分数据，适合作为默认参考\n"

        if metrics['within_3sigma'] > 99:
            result += "  ✅ 数据分布接近正态，3σ区间是合理选择\n"
        else:
            result += "  ℹ 数据分布有偏，建议使用稳健区间或百分位区间\n"

        if metrics['within_6sigma'] > 99.9:
            result += "  ✅ 数据质量很高，6σ区间可作为严格标准\n"

        return result
