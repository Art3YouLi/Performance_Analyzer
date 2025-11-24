#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:26

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Dict
from utils.config import FEISHU_COLORS, CHART_STYLE, FONT_CONFIG


class ChartRenderer:
    def __init__(self):
        # 设置matplotlib样式
        self.setup_style()

    def setup_style(self):
        """设置matplotlib样式"""
        plt.rcParams.update({
            'figure.facecolor': FEISHU_COLORS['background'],
            'axes.facecolor': FEISHU_COLORS['card'],
            'axes.edgecolor': FEISHU_COLORS['info'],
            'axes.labelcolor': FEISHU_COLORS['text_primary'],
            'text.color': FEISHU_COLORS['text_primary'],
            'xtick.color': FEISHU_COLORS['text_secondary'],
            'ytick.color': FEISHU_COLORS['text_secondary'],
            'grid.color': CHART_STYLE['grid_color'],
            'grid.alpha': CHART_STYLE['grid_alpha'],
            'font.family': FONT_CONFIG['family'],
            'font.size': FONT_CONFIG['ticks_size']
        })

    def create_figure(self, figsize=(7, 5)):
        """减小尺寸以适应显示区域"""
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(FEISHU_COLORS['background'])
        ax.set_facecolor(FEISHU_COLORS['card'])

        # 设置边框颜色
        for spine in ax.spines.values():
            spine.set_color(FEISHU_COLORS['info'])
            spine.set_linewidth(0.8)

        return fig, ax

    def plot_line_chart(self, data: List[float], parent_frame):
        """绘制折线图 - 优化布局"""
        fig, ax = self.create_figure((7, 4.5))

        time_points = range(len(data))

        # 主趋势线
        ax.plot(time_points, data, color=FEISHU_COLORS['primary'],
                linewidth=1.8, alpha=0.9, marker='', markersize=1)

        # 添加移动平均线
        window_size = min(20, len(data) // 10)
        if window_size > 1:
            moving_avg = np.convolve(data, np.ones(window_size) / window_size, mode='valid')
            ax.plot(time_points[window_size - 1:], moving_avg,
                    color=FEISHU_COLORS['danger'], linewidth=2,
                    label=f'{window_size}点移动平均', alpha=0.9)

        ax.set_xlabel('样本序列', fontsize=FONT_CONFIG['label_size'] - 1,
                      fontweight='600', color=FEISHU_COLORS['text_primary'])
        ax.set_ylabel('数值', fontsize=FONT_CONFIG['label_size'] - 1,
                      fontweight='600', color=FEISHU_COLORS['text_primary'])
        ax.set_title('数据趋势图', fontsize=FONT_CONFIG['title_size'] - 1,
                     fontweight='700', color=FEISHU_COLORS['text_primary'], pad=15)

        if window_size > 1:
            ax.legend(frameon=True, framealpha=0.9, edgecolor=FEISHU_COLORS['info'],
                      prop={'family': FONT_CONFIG['family'], 'size': FONT_CONFIG['ticks_size'] - 1})

        ax.grid(True, alpha=CHART_STYLE['grid_alpha'])

        # 使用紧凑布局
        plt.tight_layout(pad=2.0)
        self._embed_chart(fig, parent_frame)

    def plot_histogram(self, data: List[float], metrics: Dict[str, float], parent_frame):
        """绘制直方图 - 添加综合区间"""
        fig, ax = self.create_figure((7, 4.5))

        # 绘制直方图
        n, bins, patches = ax.hist(data, bins=20, alpha=0.85, color=FEISHU_COLORS['primary'],
                                   edgecolor=FEISHU_COLORS['card'], linewidth=1)

        # 标记关键指标
        ax.axvline(metrics['mean'], color=FEISHU_COLORS['primary'],
                   linestyle='--', alpha=0.9, linewidth=2,
                   label=f"平均值: {metrics['mean']:.2f}")

        # 根据数据量决定显示内容
        if 'insufficient_data' not in metrics:
            ax.axvline(metrics['p50'], color=FEISHU_COLORS['success'],
                       linestyle='--', alpha=0.9, linewidth=2,
                       label=f"P50: {metrics['p50']:.2f}")
            ax.axvline(metrics['p95'], color=FEISHU_COLORS['warning'],
                       linestyle='--', alpha=0.9, linewidth=2,
                       label=f"P95: {metrics['p95']:.2f}")

            # 添加西格玛范围
            if 'sigma_3_lower' in metrics:
                ax.axvline(metrics['sigma_3_lower'], color=FEISHU_COLORS['info'],
                           linestyle=':', alpha=0.7, linewidth=1.5,
                           label=f"3σ下限: {metrics['sigma_3_lower']:.2f}")
                ax.axvline(metrics['sigma_3_upper'], color=FEISHU_COLORS['info'],
                           linestyle=':', alpha=0.7, linewidth=1.5,
                           label=f"3σ上限: {metrics['sigma_3_upper']:.2f}")

                # 添加推荐区间
                ax.axvspan(metrics['recommended_lower'], metrics['recommended_upper'],
                           alpha=0.2, color=FEISHU_COLORS['success'],
                           label=f"推荐区间: [{metrics['recommended_lower']:.2f}, {metrics['recommended_upper']:.2f}]")

        ax.set_xlabel('数值', fontsize=FONT_CONFIG['label_size'] - 1,
                      fontweight='600', color=FEISHU_COLORS['text_primary'])
        ax.set_ylabel('频数', fontsize=FONT_CONFIG['label_size'] - 1,
                      fontweight='600', color=FEISHU_COLORS['text_primary'])

        # 根据数据量设置标题
        if 'insufficient_data' in metrics:
            ax.set_title('数据分布直方图 (数据量不足)', fontsize=FONT_CONFIG['title_size'] - 1,
                         fontweight='700', color=FEISHU_COLORS['warning'], pad=15)
        else:
            ax.set_title('数据分布直方图', fontsize=FONT_CONFIG['title_size'] - 1,
                         fontweight='700', color=FEISHU_COLORS['text_primary'], pad=15)

        ax.legend(frameon=True, framealpha=0.9, edgecolor=FEISHU_COLORS['info'],
                  prop={'family': FONT_CONFIG['family'], 'size': FONT_CONFIG['ticks_size'] - 1})
        ax.grid(True, alpha=CHART_STYLE['grid_alpha'])

        # 使用紧凑布局
        plt.tight_layout(pad=2.0)
        self._embed_chart(fig, parent_frame)

    def plot_boxplot(self, data: List[float], metrics: Dict[str, float], parent_frame):
        """绘制箱线图 - 优化布局"""
        fig, ax = self.create_figure((7, 4.5))

        box_plot = ax.boxplot(data, vert=True, patch_artist=True, widths=0.6,
                              boxprops=dict(linewidth=1.2),
                              whiskerprops=dict(linewidth=1.2),
                              capprops=dict(linewidth=1.2),
                              medianprops=dict(color=FEISHU_COLORS['danger'], linewidth=2))

        # 设置箱体颜色
        box_plot['boxes'][0].set_facecolor(FEISHU_COLORS['primary'])
        box_plot['boxes'][0].set_alpha(0.8)
        box_plot['boxes'][0].set_edgecolor(FEISHU_COLORS['info'])

        # 添加标注
        median_value = metrics.get('p50', metrics.get('median', 0))
        ax.text(1.3, median_value, f'中位数: {median_value:.2f}', va='center',
                fontsize=9, fontweight='600', color=FEISHU_COLORS['text_primary'],
                fontfamily=FONT_CONFIG['family'])

        ax.set_ylabel('数值', fontsize=FONT_CONFIG['label_size'] - 1,
                      fontweight='600', color=FEISHU_COLORS['text_primary'])

        # 根据数据量设置标题
        if 'insufficient_data' in metrics:
            ax.set_title('数据箱线图 (数据量不足)', fontsize=FONT_CONFIG['title_size'] - 1,
                         fontweight='700', color=FEISHU_COLORS['warning'], pad=15)
        else:
            ax.set_title('数据箱线图', fontsize=FONT_CONFIG['title_size'] - 1,
                         fontweight='700', color=FEISHU_COLORS['text_primary'], pad=15)

        ax.set_xticklabels(['数据分布'], fontweight='600', fontfamily=FONT_CONFIG['family'])
        ax.grid(True, alpha=CHART_STYLE['grid_alpha'])

        # 使用紧凑布局
        plt.tight_layout(pad=2.0)
        self._embed_chart(fig, parent_frame)

    def _embed_chart(self, fig, parent_frame):
        """将图表嵌入到GUI - 优化布局"""
        for widget in parent_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()

        # 使用grid布局并设置权重，确保图表能够扩展和收缩
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # 设置父容器的行列权重，确保图表能够正确扩展
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
