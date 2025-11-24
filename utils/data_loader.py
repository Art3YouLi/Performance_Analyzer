#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Zeven.Fang
# datetime: 2025/11/17 11:09

import re
from typing import List, Dict


class DataLoader:
    def __init__(self):
        self.data_sets = {}

    def load_data_file(self, filename: str, data_type: str) -> List[float]:
        """加载数据文件，支持多种格式"""
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试解析hogs指令输出格式
            if self._is_hogs_format(content):
                data = self._parse_hogs_output(content, data_type)
            else:
                # 普通文本格式，每行一个数值
                data = self._parse_text_format(content)

        except Exception as e:
            raise Exception(f"读取文件时出错: {str(e)}")

        return data

    def _is_hogs_format(self, content: str) -> bool:
        """检测是否为hogs指令输出格式"""
        # hogs格式通常包含进程信息和资源占用
        hogs_patterns = [
            r'PID.*USER.*COMMAND',
            r'\d+\.\d+%.*\d+\.\d+%',  # 百分比格式
            r'\d+/\d+.*\d+\.\d+%',  # 进程数/总进程数 百分比
        ]

        for pattern in hogs_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True
        return False

    def _parse_hogs_output(self, content: str, data_type: str) -> List[float]:
        """解析hogs指令输出"""
        data = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 跳过表头
            if any(header in line for header in ['PID', 'USER', 'COMMAND', 'CPU', 'MEM']):
                continue

            # 提取数值
            values = self._extract_values_from_line(line, data_type)
            if values:
                data.extend(values)

        return data

    def _extract_values_from_line(self, line: str, data_type: str) -> List[float]:
        """从行中提取数值"""
        values = []

        # 根据数据类型提取相应的数值
        if data_type == "CPU占用值":
            # 查找CPU百分比，如 "10.5%"
            cpu_matches = re.findall(r'(\d+\.?\d*)%\s*(?=\d*\.?\d*%|$)', line)
            if cpu_matches:
                values = [float(match) for match in cpu_matches if match]
        elif data_type in ["内存占用峰值", "内存占用均值"]:
            # 查找内存百分比或MB值
            mem_matches = re.findall(r'(\d+\.?\d*)(?:%|MB|GB)', line)
            if mem_matches:
                values = [float(match) for match in mem_matches if match]
        else:
            # 对于其他数据类型，尝试提取所有数字
            num_matches = re.findall(r'(\d+\.?\d*)', line)
            if num_matches:
                values = [float(match) for match in num_matches if match]

        return values

    def _parse_text_format(self, content: str) -> List[float]:
        """解析普通文本格式"""
        data = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line:
                try:
                    # 尝试将每行转换为浮点数
                    value = float(line)
                    data.append(value)
                except ValueError:
                    # 如果转换失败，尝试处理可能包含逗号或其他分隔符的情况
                    parts = line.split()
                    for part in parts:
                        try:
                            value = float(part)
                            data.append(value)
                        except ValueError:
                            continue
        return data

    def set_data(self, data_type: str, data: List[float]):
        """设置数据"""
        self.data_sets[data_type] = data

    def get_data(self, data_type: str) -> List[float]:
        """获取数据"""
        return self.data_sets.get(data_type, [])

    def has_data(self, data_type: str) -> bool:
        """检查是否有数据"""
        return len(self.get_data(data_type)) > 0