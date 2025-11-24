#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/13 10:24

# 配置文件
import matplotlib.pyplot as plt

# 设置中文字体和图表样式 - 统一使用微软雅黑
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 配色方案
FEISHU_COLORS = {
    "primary": "#3370FF",      # 主蓝色
    "success": "#00B968",      # 成功绿色
    "warning": "#FF9D00",      # 警告橙色
    "danger": "#F53F3F",       # 危险红色
    "info": "#86909C",         # 信息灰色
    "background": "#F7F8FA",   # 背景浅灰
    "card": "#FFFFFF",         # 卡片白色
    "text_primary": "#1D2129", # 主要文字
    "text_secondary": "#86909C" # 次要文字
}

# 字体配置
FONT_CONFIG = {
    "family": "Microsoft YaHei",
    "title_size": 14,
    "label_size": 11,
    "ticks_size": 10,
    "button_size": 10,
    "text_size": 9
}

# 图表样式配置
CHART_STYLE = {
    "background_color": FEISHU_COLORS["background"],
    "grid_color": "#E5E6EB",
    "grid_alpha": 0.3,
    "font_family": FONT_CONFIG["family"],
    "title_size": FONT_CONFIG["title_size"],
    "label_size": FONT_CONFIG["label_size"],
    "ticks_size": FONT_CONFIG["ticks_size"]
}

# 支持的图表类型
CHART_TYPES = ["折线图", "直方图", "箱线图"]
