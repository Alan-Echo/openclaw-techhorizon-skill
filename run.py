#!/usr/bin/env python3
"""
TechHorizon 主执行脚本 - 更新版（移除Gitee数据源）
"""

import sys
import os
# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from techhorizon.collectors_updated import collect_all_sources

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='TechHorizon - IT/编程/科技技术界情报收集分析')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly'], 
                       default='daily', help='运行模式')
    parser.add_argument('--output', help='输出文件路径')
    args = parser.parse_args()
    
    if args.mode == 'daily':
        from techhorizon.processor import DataProcessor
        from techhorizon.storage import DataStorage
        processor = DataProcessor()
        storage = DataStorage()
        
        # 收集原始数据
        raw_events = collect_all_sources()
        print(f"收集到 {len(raw_events)} 条原始事件")
        
        # 处理数据
        processed_events = processor.process_events(raw_events)
        unique_events = processor.remove_duplicates(processed_events)
        
        # 保存和输出
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = {
            'date': today,
            'collection_time': datetime.now().isoformat(),
            'total_raw_events': len(raw_events),
            'total_processed_events': len(processed_events),
            'total_unique_events': len(unique_events),
            'events': unique_events
        }
        
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, ensure_ascii=False, indent=2)
        else:
            import json
            print(json.dumps(daily_data, ensure_ascii=False))

if __name__ == "__main__":
    main()