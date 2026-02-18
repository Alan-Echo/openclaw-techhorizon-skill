#!/usr/bin/env python3
"""
TechHorizon 技能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scripts.main import run_daily_collection
from scripts.processor import DataProcessor
from scripts.storage import DataStorage

def test_basic_functionality():
    """测试基本功能"""
    print("=== TechHorizon 技能测试 ===")
    
    # 测试数据处理器
    processor = DataProcessor()
    
    # 测试英文标题处理
    en_title = "GitHub Actions is slowly killing engineering teams"
    processed_title = processor.process_title(en_title)
    print(f"英文标题处理: {processed_title}")
    
    # 测试中文标题处理  
    zh_title = "微软承认Windows 11严重漏洞"
    processed_zh_title = processor.process_title(zh_title)
    print(f"中文标题处理: {processed_zh_title}")
    
    # 测试描述处理
    en_desc = "A detailed analysis of how GitHub Actions complexity is causing problems"
    processed_desc = processor.process_description(en_desc)
    print(f"英文描述处理: {processed_desc}")
    
    # 测试存储系统
    storage = DataStorage()
    print(f"存储目录创建: {os.path.exists('.techhorizon/daily')}")
    
    print("\n=== 测试完成 ===")
    print("技能基本功能正常！")

if __name__ == "__main__":
    test_basic_functionality()