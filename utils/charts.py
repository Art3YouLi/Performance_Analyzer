#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:26

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Dict
from utils.config import FEISHU_COLORS, CHART_STYLE, FONT_CONFIG, SAFE_ICONS


class ChartRenderer:
    def __init__(self):
        # 设置matplotlib样式
        self.setup_style()

    def setup_style(self):
        """设置matplotlib样式 - 优化美观度"""
        plt.rcParams.update({
            'figure.facecolor': FEISHU_COLORS['background'],
            'axes.facecolor': FEISHU_COLORS['card'],
            'axes.edgecolor': FEISHU_COLORS['info'],
            'axes.labelcolor': FEISHU_COLORS['text_primary'],
            'text.color': FEISHU_COLORS['text_primary'],
            'xtick.color': FEISHU_COLORS['text_secondary'],
            'ytick.color': FEISHU_COLORS['text_secondary'],
            'grid.color': CHART_STYLE['grid_color'],
            'grid.alpha': 0.5,
            'grid.linestyle': '--',
            'font.family': FONT_CONFIG['family'],
            'font.size': FONT_CONFIG['ticks_size'],
            'axes.titlesize': FONT_CONFIG['title_size'],
            'axes.labelsize': FONT_CONFIG['label_size'],
            'xtick.labelsize': FONT_CONFIG['ticks_size'] - 1,
            'ytick.labelsize': FONT_CONFIG['ticks_size'] - 1,
            'legend.fontsize': FONT_CONFIG['ticks_size'] - 1,
            'legend.framealpha': 0.9,
            'legend.edgecolor': FEISHU_COLORS['info'],
        })

    def create_figure(self, figsize=(8, 5.5)):
        """创建图表 - 优化尺寸和样式"""
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
        fig.patch.set_facecolor(FEISHU_COLORS['background'])
        ax.set_facecolor(FEISHU_COLORS['card'])

        # 设置边框颜色和粗细
        for spine in ax.spines.values():
            spine.set_color(FEISHU_COLORS['info'])
            spine.set_linewidth(1.2)

        return fig, ax

    def plot_line_chart(self, file_datasets: Dict[str, List[float]], parent_frame):
        """绘制折线图 - 优化美观度"""
        fig, ax = self.create_figure((8, 5.5))

        # 优化的颜色列表
        colors = [
            '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
            '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
        ]

        if len(file_datasets) > 1:
            # 多文件对比模式 - 优化样式
            for i, (filename, file_data) in enumerate(file_datasets.items()):
                if len(file_data) == 0:
                    continue

                time_points = np.arange(len(file_data))
                color = colors[i % len(colors)]
                short_name = filename.split('/')[-1]
                label = f"{short_name} ({len(file_data)}点)"

                # 绘制主趋势线 - 优化线条样式
                ax.plot(time_points, file_data, color=color, linewidth=2.0,
                        alpha=0.85, label=label, marker='', markersize=0)

                # 为数据量大的文件添加平滑曲线
                if len(file_data) > 50:
                    # 使用移动平均创建平滑曲线
                    window_size = min(10, len(file_data) // 20)
                    if window_size > 1:
                        kernel = np.ones(window_size) / window_size
                        smoothed = np.convolve(file_data, kernel, mode='valid')
                        ax.plot(time_points[window_size - 1:], smoothed,
                                color=color, linewidth=2.5, linestyle='-',
                                alpha=0.7, label=f'{short_name} - 平滑')

            # 优化图例
            ax.legend(frameon=True, framealpha=0.95, edgecolor=FEISHU_COLORS['info'],
                      loc='upper left', bbox_to_anchor=(1.02, 1),
                      borderaxespad=0., facecolor=FEISHU_COLORS['card'])

            title = f'趋势图 - 多文件数据对比 ({len(file_datasets)}个文件)'
        else:
            # 单文件模式 - 优化样式
            filename, data = list(file_datasets.items())[0]
            if len(data) == 0:
                self._show_no_data_message(fig, ax, parent_frame)
                return

            time_points = np.arange(len(data))
            short_name = filename.split('/')[-1]

            # 主趋势线 - 优化样式
            ax.plot(time_points, data, color=FEISHU_COLORS['primary'],
                    linewidth=2.5, alpha=0.9, marker='', markersize=0)

            # 添加平滑趋势线
            if len(data) > 20:
                window_size = min(15, len(data) // 10)
                kernel = np.ones(window_size) / window_size
                smoothed = np.convolve(data, kernel, mode='valid')

                ax.plot(time_points[window_size - 1:], smoothed,
                        color=FEISHU_COLORS['danger'], linewidth=3.0,
                        label='平滑趋势线', alpha=0.8)

                ax.legend(frameon=True, framealpha=0.95, edgecolor=FEISHU_COLORS['info'],
                          facecolor=FEISHU_COLORS['card'])

            title = f'{short_name} - 数据趋势分析'

        # 优化坐标轴标签
        ax.set_xlabel('样本序列', fontweight='600', color=FEISHU_COLORS['text_primary'])
        ax.set_ylabel('数值', fontweight='600', color=FEISHU_COLORS['text_primary'])

        # 优化标题
        ax.set_title(title, fontsize=FONT_CONFIG['title_size'],
                     fontweight='700', color=FEISHU_COLORS['text_primary'], pad=20)

        # 优化网格
        ax.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)

        # 调整布局
        if len(file_datasets) > 1:
            plt.tight_layout(rect=[0, 0, 0.85, 1])
        else:
            plt.tight_layout()

        self._embed_chart(fig, parent_frame)

    def plot_histogram(self, file_datasets: Dict[str, List[float]], file_metrics: Dict[str, Dict], parent_frame):
        """绘制直方图 - 优化美观度"""
        fig, ax = self.create_figure((8, 5.5))

        # 优化的颜色列表
        colors = [
            '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
            '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
        ]

        if len(file_datasets) > 1:
            # 多文件对比模式 - 优化样式
            all_data = []
            for file_data in file_datasets.values():
                all_data.extend(file_data)

            if len(all_data) == 0:
                self._show_no_data_message(fig, ax, parent_frame)
                return

            # 计算优化的bins
            bins = np.histogram_bin_edges(all_data, bins=min(25, len(all_data) // 15))

            for i, (filename, file_data) in enumerate(file_datasets.items()):
                if len(file_data) == 0:
                    continue

                color = colors[i % len(colors)]
                short_name = filename.split('/')[-1]

                # 绘制直方图 - 优化样式
                n, bins, patches = ax.hist(file_data, bins=bins, alpha=0.7, color=color,
                                           edgecolor='white', linewidth=1.2, label=short_name)

            # 优化图例
            ax.legend(frameon=True, framealpha=0.95, edgecolor=FEISHU_COLORS['info'],
                      loc='upper left', bbox_to_anchor=(1.02, 1),
                      borderaxespad=0., facecolor=FEISHU_COLORS['card'])

            title = f'分布图 - 多文件数据对比 ({len(file_datasets)}个文件)'
        else:
            # 单文件模式 - 优化样式
            filename, data = list(file_datasets.items())[0]
            if len(data) == 0:
                self._show_no_data_message(fig, ax, parent_frame)
                return

            metrics = file_metrics[filename]
            short_name = filename.split('/')[-1]

            # 计算优化的bins
            bins = min(20, max(10, len(data) // 20))

            # 绘制直方图 - 优化样式
            n, bins, patches = ax.hist(data, bins=bins, alpha=0.85,
                                       color=FEISHU_COLORS['primary'],
                                       edgecolor='white', linewidth=1.5)

            # 标记关键指标 - 优化样式
            if 'insufficient_data' not in metrics:
                # 平均值线
                ax.axvline(metrics['mean'], color=FEISHU_COLORS['primary'],
                           linestyle='-', alpha=0.9, linewidth=3,
                           label=f"平均值: {metrics['mean']:.2f}")

                # 中位数线
                ax.axvline(metrics['p50'], color=FEISHU_COLORS['success'],
                           linestyle='--', alpha=0.9, linewidth=2.5,
                           label=f"中位数: {metrics['p50']:.2f}")

                # P95线
                ax.axvline(metrics['p95'], color=FEISHU_COLORS['warning'],
                           linestyle='-.', alpha=0.9, linewidth=2,
                           label=f"P95: {metrics['p95']:.2f}")

                # 添加西格玛范围背景
                if 'sigma_3_lower' in metrics:
                    ax.axvspan(metrics['sigma_3_lower'], metrics['sigma_3_upper'],
                               alpha=0.15, color=FEISHU_COLORS['info'],
                               label='3σ范围')

            ax.legend(frameon=True, framealpha=0.95, edgecolor=FEISHU_COLORS['info'],
                      facecolor=FEISHU_COLORS['card'])

            title = f'{short_name} - 数据分布分析'

        # 优化坐标轴标签
        ax.set_xlabel('数值', fontweight='600', color=FEISHU_COLORS['text_primary'])
        ax.set_ylabel('频数', fontweight='600', color=FEISHU_COLORS['text_primary'])

        # 优化标题
        ax.set_title(title, fontsize=FONT_CONFIG['title_size'],
                     fontweight='700', color=FEISHU_COLORS['text_primary'], pad=20)

        # 优化网格
        ax.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)

        # 调整布局
        if len(file_datasets) > 1:
            plt.tight_layout(rect=[0, 0, 0.85, 1])
        else:
            plt.tight_layout()

        self._embed_chart(fig, parent_frame)

    def plot_boxplot(self, file_datasets: Dict[str, List[float]], file_metrics: Dict[str, Dict], parent_frame):
        """绘制箱线图 - 优化美观度"""
        fig, ax = self.create_figure((8, 5.5))

        # 过滤掉空数据集
        valid_datasets = {k: v for k, v in file_datasets.items() if len(v) > 0}

        if len(valid_datasets) == 0:
            self._show_no_data_message(fig, ax, parent_frame)
            return

        # 优化的颜色列表
        colors = [
            '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
            '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
        ]

        if len(valid_datasets) > 1:
            # 多文件对比模式 - 优化样式
            data_arrays = list(valid_datasets.values())
            labels = [filename.split('/')[-1][:20] for filename in valid_datasets.keys()]

            # 创建箱线图 - 优化样式
            box_plot = ax.boxplot(data_arrays, labels=labels, vert=True, patch_artist=True, widths=0.7,
                                  boxprops=dict(linewidth=2.0, alpha=0.8),
                                  whiskerprops=dict(linewidth=1.8),
                                  capprops=dict(linewidth=1.8),
                                  medianprops=dict(color=FEISHU_COLORS['danger'], linewidth=2.5),
                                  flierprops=dict(marker='o', markersize=4, alpha=0.6, markerfacecolor='red'))

            # 设置箱体颜色 - 优化颜色
            for i, box in enumerate(box_plot['boxes']):
                box.set_facecolor(colors[i % len(colors)])
                box.set_edgecolor(colors[i % len(colors)])

            title = f'箱线图 - 多文件数据对比 ({len(valid_datasets)}个文件)'
        else:
            # 单文件模式 - 优化样式
            filename, data = list(valid_datasets.items())[0]
            metrics = file_metrics[filename]
            short_name = filename.split('/')[-1]

            # 创建箱线图 - 优化样式
            box_plot = ax.boxplot(data, vert=True, patch_artist=True, widths=0.6,
                                  boxprops=dict(linewidth=2.0, alpha=0.8),
                                  whiskerprops=dict(linewidth=1.8),
                                  capprops=dict(linewidth=1.8),
                                  medianprops=dict(color=FEISHU_COLORS['danger'], linewidth=2.5))

            # 设置箱体颜色
            box_plot['boxes'][0].set_facecolor(FEISHU_COLORS['primary'])
            box_plot['boxes'][0].set_edgecolor(FEISHU_COLORS['primary'])

            # 添加统计标注 - 优化样式
            stats_text = f'''统计摘要:
平均值: {metrics['mean']:.2f}
中位数: {metrics['p50']:.2f}
Q1: {metrics.get('p25', metrics['p50']):.2f}
Q3: {metrics.get('p75', metrics['p50']):.2f}
P95: {metrics['p95']:.2f}'''

            # 在图表右侧添加文本
            ax.text(1.35, 0.5, stats_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='center', bbox=dict(boxstyle="round,pad=0.5",
                                                          facecolor=FEISHU_COLORS['background'], alpha=0.8))

            title = f'{short_name} - 数据分布箱线图'

        ax.set_ylabel('数值', fontweight='600', color=FEISHU_COLORS['text_primary'])

        # 优化标题
        ax.set_title(title, fontsize=FONT_CONFIG['title_size'],
                     fontweight='700', color=FEISHU_COLORS['text_primary'], pad=20)

        # 旋转x轴标签以避免重叠
        if len(valid_datasets) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # 优化网格
        ax.grid(True, alpha=0.6, linestyle='--', linewidth=0.8, axis='y')

        plt.tight_layout()
        self._embed_chart(fig, parent_frame)

    def _show_no_data_message(self, fig, ax, parent_frame):
        """显示无数据消息 - 优化样式"""
        ax.text(0.5, 0.5, '无有效数据可显示',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=16, color=FEISHU_COLORS['text_secondary'],
                fontweight='600')
        ax.text(0.5, 0.4, '请加载包含有效数据的数据文件',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12, color=FEISHU_COLORS['text_secondary'])
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self._embed_chart(fig, parent_frame)

    def _embed_chart(self, fig, parent_frame):
        """将图表嵌入到GUI - 优化嵌入方式"""
        for widget in parent_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()

        # 使用grid布局并设置权重，确保图表能够扩展和收缩
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # 设置父容器的行列权重，确保图表能够正确扩展
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
