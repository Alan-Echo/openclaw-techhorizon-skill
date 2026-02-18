#!/usr/bin/env python3
"""
TechHorizon 文件存储和管理模块
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List

class DataStorage:
    """数据存储管理器"""
    
    def __init__(self, base_dir: str = ".techhorizon"):
        self.base_dir = base_dir
        self.setup_directories()
        
        # 保留策略配置
        self.retention_policy = {
            'daily': 30,      # 天
            'weekly': 52,     # 周  
            'monthly': 24,    # 月
            'cache': 7        # 天
        }
    
    def setup_directories(self):
        """创建必要的目录结构"""
        directories = [
            f"{self.base_dir}/daily",
            f"{self.base_dir}/weekly", 
            f"{self.base_dir}/monthly",
            f"{self.base_dir}/cache",
            f"{self.base_dir}/metadata"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_daily_data(self, date: str, data: Dict[str, Any]):
        """保存每日数据"""
        file_path = f"{self.base_dir}/daily/{date}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_weekly_report(self, week: str, report: Dict[str, Any]):
        """保存周度报告"""
        file_path = f"{self.base_dir}/weekly/{week}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def save_monthly_report(self, month: str, report: Dict[str, Any]):
        """保存月度报告"""
        file_path = f"{self.base_dir}/monthly/{month}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def load_daily_data(self, date: str) -> Dict[str, Any]:
        """加载每日数据"""
        file_path = f"{self.base_dir}/daily/{date}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_all_daily_files(self) -> List[str]:
        """获取所有每日数据文件"""
        daily_dir = f"{self.base_dir}/daily"
        if not os.path.exists(daily_dir):
            return []
        return [f for f in os.listdir(daily_dir) if f.endswith('.json')]
    
    def cleanup_old_files(self):
        """清理过期文件"""
        current_time = datetime.now()
        
        # 清理每日数据
        self._cleanup_by_retention('daily', self.retention_policy['daily'])
        
        # 清理周报
        self._cleanup_by_retention('weekly', self.retention_policy['weekly'] * 7)
        
        # 清理月报  
        self._cleanup_by_retention('monthly', self.retention_policy['monthly'] * 30)
        
        # 清理缓存
        self._cleanup_by_retention('cache', self.retention_policy['cache'])
    
    def _cleanup_by_retention(self, data_type: str, days: int):
        """按保留策略清理文件"""
        directory = f"{self.base_dir}/{data_type}"
        if not os.path.exists(directory):
            return
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"Deleted old {data_type} file: {filename}")
                    except OSError as e:
                        print(f"Failed to delete {filename}: {e}")
    
    def get_total_storage_size(self) -> int:
        """获取总存储大小（字节）"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.base_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size