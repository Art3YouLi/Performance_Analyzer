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

    def calculate_performance_metrics(self, data: List[float]) -> Dict[str, float]:
        """计算性能指标 - 简化版本，只计算核心指标"""
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

        # 计算标准差（总是计算）
        metrics['std'] = np.std(data)

        # 西格玛水平计算 (数据量 >= 30)
        if data_count >= self.min_sigma_threshold:
            sigma_metrics = self._calculate_sigma_levels(data, metrics['mean'], metrics['std'])
            metrics.update(sigma_metrics)
        else:
            metrics['sigma_status'] = f'数据量不足 ({data_count} < {self.min_sigma_threshold})'

        # 数据质量评估
        metrics.update(self._assess_data_quality(data_count))

        return metrics

    def _calculate_sigma_levels(self, data: List[float], mean: float, std: float) -> Dict[str, float]:
        """计算西格玛水平 - 只计算3sigma和6sigma"""
        sigma_levels = {}

        if std == 0:
            return {
                'sigma_3_lower': mean,
                'sigma_3_upper': mean,
                'sigma_6_lower': mean,
                'sigma_6_upper': mean,
                'within_3sigma': 100.0,
                'within_6sigma': 100.0,
            }

        # 3sigma范围计算
        sigma_3_lower = mean - 3 * std
        sigma_3_upper = mean + 3 * std

        # 6sigma范围计算
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
        """生成分析报告 - 简化版本"""
        result = "┌" + "─" * 58 + "┐\n"
        result += f" {filename:^56} \n"
        result += "└" + "─" * 58 + "┘\n\n"

        # 数据概览
        data_count = metrics['count']
        data_quality = metrics.get('data_quality', '未知')

        result += f"数据概览: {data_count} 个样本 ({data_quality})\n"
        result += "─" * 40 + "\n"

        # 数据量严重不足的情况
        if metrics.get('insufficient_data', False) and data_count < 10:
            result += "\n⚠️  数据量严重不足\n"
            result += "   当前数据量无法进行有效的统计分析\n"
            result += "   建议收集更多数据以获得可靠分析结果\n\n"

            result += "基础统计 (仅供参考):\n"
            result += f"   平均值: {metrics['mean']:.2f}\n"
            result += f"   中位数: {metrics['median']:.2f}\n"
            result += f"   最小值: {metrics['min']:.2f}\n"
            result += f"   最大值: {metrics['max']:.2f}\n"
            return result

        # 数据量提示
        if metrics.get('insufficient_data', False):
            result += "⚠️  数据量较少，部分分析受限\n\n"

        # 核心统计指标
        result += "核心统计指标:\n"
        result += f"   平均值: {metrics['mean']:.2f}\n"
        result += f"   中位数: {metrics['median']:.2f}\n"
        result += f"   标准差: {metrics.get('std', 0):.2f}\n"
        result += f"   数据范围: [{metrics['min']:.2f}, {metrics['max']:.2f}]\n\n"

        if 'std' in metrics:
            # 西格玛分析
            if 'sigma_3_lower' in metrics:
                result += self._generate_sigma_analysis(metrics)
            elif 'sigma_status' in metrics:
                result += f"西格玛分析: {metrics['sigma_status']}\n\n"
        else:
            result += "数据量不足，无法计算标准差和西格玛指标\n\n"

        return result

    def _generate_sigma_analysis(self, metrics: Dict[str, float]) -> str:
        """生成西格玛分析报告 - 只显示3sigma和6sigma"""
        result = "西格玛区间分析:\n"

        sigma_3_lower = metrics.get('sigma_3_lower')
        sigma_3_upper = metrics.get('sigma_3_upper')
        sigma_6_lower = metrics.get('sigma_6_lower')
        sigma_6_upper = metrics.get('sigma_6_upper')

        if sigma_3_lower is not None and sigma_3_upper is not None:
            result += f"   3σ区间: [{sigma_3_lower:.2f}, {sigma_3_upper:.2f}] "
            result += f"({metrics.get('within_3sigma', 0):.1f}%数据)\n"

        if sigma_6_lower is not None and sigma_6_upper is not None:
            result += f"   6σ区间: [{sigma_6_lower:.2f}, {sigma_6_upper:.2f}] "
            result += f"({metrics.get('within_6sigma', 0):.1f}%数据)\n"

        result += "\n"
        return result
