#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/17 11:07

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.filedialog as fd
import tkinter.messagebox as messagebox
from utils.data_loader import DataLoader
from utils.analyzer import PerformanceAnalyzer
from utils.charts import ChartRenderer
from utils.config import FEISHU_COLORS, FONT_CONFIG, CHART_TYPES


class PerformanceAnalyzerApp:
    def __init__(self):
        # 使用浅色主题
        self.notebook = None
        self.result_text = None
        self.analyze_btn = None
        self.load_btn = None
        self.file_path = None
        self.status_label = None
        self.chart_tabs = None
        self.root = ttk.Window(
            title="性能分析工具",
            themename="journal",
            size=(1400, 900),
            minsize=(1200, 700)
        )

        # 自定义风格颜色和字体
        self.setup_feishu_style()

        # 初始化组件
        self.data_loader = DataLoader()
        self.analyzer = PerformanceAnalyzer()
        self.chart_renderer = ChartRenderer()

        # 当前数据
        self.current_data = []
        self.metrics = {}

        self.setup_ui()

    def setup_feishu_style(self):
        """设置自定义样式和字体"""
        style = ttk.Style()

        # 设置全局字体为微软雅黑
        self.root.option_add('*Font', (FONT_CONFIG['family'], FONT_CONFIG['text_size']))

    def setup_ui(self):
        """设置用户界面 - 优化布局"""
        # 创建主容器
        main_container = ttk.Frame(self.root, padding=0)
        main_container.pack(fill=BOTH, expand=True)

        # 设置主容器的行列权重
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # 顶部标题栏
        self.create_header(main_container)

        # 主要内容区域 - 三模块布局
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=BOTH, expand=True, pady=10)

        # 设置内容框架的行列权重
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        content_frame.rowconfigure(2, weight=1)

        # 模块1: 数据加载
        self.create_data_loading_module(content_frame)

        # 模块2: 分析结果
        self.create_analysis_module(content_frame)

        # 模块3: 可视化图表
        self.create_charts_module(content_frame)

    def create_header(self, parent):
        """创建顶部标题栏"""
        header_frame = ttk.Frame(parent, bootstyle=LIGHT)
        header_frame.pack(fill=X, pady=(0, 10), padx=10)

        # 标题 - 设置透明背景
        title_label = ttk.Label(
            header_frame,
            text="📊 性能数据分析工具",
            font=(FONT_CONFIG['family'], 18, 'bold'),
            foreground=FEISHU_COLORS['text_primary'],
            background=''  # 设置为透明背景
        )
        title_label.pack(side=LEFT, padx=10, pady=10)

        # 状态指示器 - 设置透明背景
        self.status_label = ttk.Label(
            header_frame,
            text="● 就绪",
            font=(FONT_CONFIG['family'], 10),
            foreground=FEISHU_COLORS['success'],
            background=''  # 设置为透明背景
        )
        self.status_label.pack(side=RIGHT, padx=10, pady=10)

    def create_data_loading_module(self, parent):
        """创建数据加载模块"""
        loading_frame = ttk.Labelframe(
            parent,
            text="📁 数据加载",
            bootstyle=INFO,
            padding=15
        )
        loading_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        loading_frame.columnconfigure(1, weight=1)  # 文件路径输入框可扩展

        # 文件路径显示
        path_label = ttk.Label(
            loading_frame,
            text="当前文件:",
            font=(FONT_CONFIG['family'], 10, 'bold'),
            foreground=FEISHU_COLORS['text_primary']
        )
        path_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        self.file_path = ttk.StringVar()
        path_entry = ttk.Entry(
            loading_frame,
            textvariable=self.file_path,
            state="readonly",
            font=(FONT_CONFIG['family'], 9)
        )
        path_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 10))

        # 按钮区域
        button_frame = ttk.Frame(loading_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='w')

        self.load_btn = ttk.Button(
            button_frame,
            text="📂 加载数据文件",
            command=self.load_file,
            bootstyle=PRIMARY,
            width=20
        )
        self.load_btn.pack(side=LEFT, padx=(0, 10))

        self.analyze_btn = ttk.Button(
            button_frame,
            text="🔍 分析数据",
            command=self.analyze_data,
            bootstyle=SUCCESS,
            width=20
        )
        self.analyze_btn.pack(side=LEFT)

    def create_analysis_module(self, parent):
        """创建分析结果模块"""
        analysis_frame = ttk.Labelframe(
            parent,
            text="📋 分析结果",
            bootstyle=INFO,
            padding=15
        )
        analysis_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)

        # 结果文本框
        self.result_text = ttk.Text(
            analysis_frame,
            font=(FONT_CONFIG['family'], FONT_CONFIG['text_size']),
            wrap=WORD
        )

        result_scrollbar = ttk.Scrollbar(
            analysis_frame,
            orient=VERTICAL,
            command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar.grid(row=0, column=1, sticky='ns')

        # 初始显示提示信息
        self.result_text.insert(1.0, "请先加载数据文件，然后点击'分析数据'按钮")
        self.result_text.config(state=DISABLED)

    def create_charts_module(self, parent):
        """创建可视化图表模块"""
        charts_frame = ttk.Labelframe(
            parent,
            text="📊 可视化图表",
            bootstyle=INFO,
            padding=15
        )
        charts_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.rowconfigure(0, weight=1)

        # 创建笔记本（选项卡）控件
        self.notebook = ttk.Notebook(charts_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # 创建图表标签页
        self.chart_tabs = {}
        for chart_type in CHART_TYPES:
            tab = ttk.Frame(self.notebook)
            self.chart_tabs[chart_type] = tab
            self.notebook.add(tab, text=chart_type)
            # 设置标签页的布局权重
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)

    def load_file(self):
        """加载数据文件"""
        # 确保窗口更新，避免对话框被遮挡
        self.root.update()

        filename = fd.askopenfilename(
            parent=self.root,
            title="选择数据文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            self.file_path.set(filename)
            try:
                # 加载数据文件
                self.current_data = self.data_loader.load_data_file(filename, "通用数据")

                self.status_label.config(
                    text=f"● 已加载 {len(self.current_data)} 个数据点",
                    foreground=FEISHU_COLORS['success']
                )

                # 自动分析数据
                self.analyze_data()

            except Exception as e:
                self.status_label.config(
                    text="● 加载失败",
                    foreground=FEISHU_COLORS['danger']
                )
                messagebox.showerror("错误", f"读取文件时出错: {str(e)}")

    def analyze_data(self):
        """分析数据并显示结果"""
        if not self.current_data:
            self.status_label.config(
                text="● 无数据可分析",
                foreground=FEISHU_COLORS['warning']
            )
            messagebox.showwarning(
                "警告",
                "没有可分析的数据，请先加载数据文件"
            )
            return

        self.status_label.config(
            text="● 分析中...",
            foreground=FEISHU_COLORS['primary']
        )

        # 计算指标
        self.metrics = self.analyzer.calculate_performance_metrics(self.current_data)

        # 显示结果
        self.display_results()

        # 绘制图表
        self.plot_charts()

        self.status_label.config(
            text="● 分析完成",
            foreground=FEISHU_COLORS['success']
        )

    def display_results(self):
        """显示分析结果"""
        report = self.analyzer.generate_analysis_report(self.metrics)

        self.result_text.config(state=NORMAL)
        self.result_text.delete(1.0, END)
        self.result_text.insert(1.0, report)
        self.result_text.config(state=DISABLED)

    def plot_charts(self):
        """绘制所有图表"""
        for chart_type in CHART_TYPES:
            if chart_type in self.chart_tabs:
                if chart_type == "折线图":
                    self.chart_renderer.plot_line_chart(self.current_data, self.chart_tabs[chart_type])
                elif chart_type == "直方图":
                    self.chart_renderer.plot_histogram(self.current_data, self.metrics, self.chart_tabs[chart_type])
                elif chart_type == "箱线图":
                    self.chart_renderer.plot_boxplot(self.current_data, self.metrics, self.chart_tabs[chart_type])

    def run(self):
        """运行应用"""
        self.root.mainloop()
