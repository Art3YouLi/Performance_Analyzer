#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:24

import matplotlib.pyplot as plt

PROJECT_INFO = {
    'name': '性能分析工具',
    'version': '1.0.2',
    'description': '多文件性能数据分析工具'
}


# 设置中文字体和图表样式 - 优化字体回退机制
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 优化的配色方案
FEISHU_COLORS = {
    "primary": "#3370FF",      # 主蓝色
    "success": "#00B968",      # 成功绿色
    "warning": "#FF9D00",      # 警告橙色
    "danger": "#F53F3F",       # 危险红色
    "info": "#86909C",         # 信息灰色
    "background": "#F7F8FA",   # 背景浅灰
    "card": "#FFFFFF",         # 卡片白色
    "text_primary": "#1D2129", # 主要文字
    "text_secondary": "#86909C", # 次要文字
    "grid": "#E5E6EB"         # 网格线颜色
}

# 优化的字体配置 - 避免使用特殊字符
FONT_CONFIG = {
    "family": "Microsoft YaHei",
    "title_size": 14,          # 适当减小标题字体
    "label_size": 11,          # 适当减小标签字体
    "ticks_size": 9,           # 适当减小刻度字体
    "button_size": 10,
    "text_size": 9             # 适当减小文本字体
}

# 优化的图表样式配置
CHART_STYLE = {
    "background_color": FEISHU_COLORS["background"],
    "grid_color": FEISHU_COLORS["grid"],
    "grid_alpha": 0.6,
    "font_family": FONT_CONFIG["family"],
    "title_size": FONT_CONFIG["title_size"],
    "label_size": FONT_CONFIG["label_size"],
    "ticks_size": FONT_CONFIG["ticks_size"]
}

# 支持的图表类型
CHART_TYPES = ["折线图", "直方图", "箱线图"]
