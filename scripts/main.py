#!/usr/bin/env python3
"""
TechHorizon 主执行脚本
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from .collectors import collect_all_sources
from .processor import DataProcessor
from .storage import DataStorage

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TechHorizon - IT/编程/科技技术界情报收集分析')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly'], 
                       default='daily', help='运行模式')
    parser.add_argument('--output', help='输出文件路径')
    args = parser.parse_args()
    
    # 初始化组件
    processor = DataProcessor()
    storage = DataStorage()
    
    if args.mode == 'daily':
        run_daily_collection(processor, storage, args.output)
    elif args.mode == 'weekly':
        run_weekly_analysis(processor, storage, args.output)
    elif args.mode == 'monthly':
        run_monthly_analysis(processor, storage, args.output)

def run_daily_collection(processor, storage, output_file=None):
    """执行每日数据收集"""
    print("开始每日数据收集...")
    
    # 收集原始数据
    raw_events = collect_all_sources()
    print(f"收集到 {len(raw_events)} 条原始事件")
    
    # 处理数据
    processed_events = processor.process_events(raw_events)
    print(f"处理后 {len(processed_events)} 条事件")
    
    # 去重
    unique_events = processor.remove_duplicates(processed_events)
    print(f"去重后 {len(unique_events)} 条唯一事件")
    
    # 保存数据
    today = datetime.now().strftime('%Y-%m-%d')
    daily_data = {
        'date': today,
        'collection_time': datetime.now().isoformat(),
        'total_raw_events': len(raw_events),
        'total_processed_events': len(processed_events),
        'total_unique_events': len(unique_events),
        'events': unique_events
    }
    
    storage.save_daily_data(today, daily_data)
    print(f"已保存每日数据到 .techhorizon/daily/{today}.json")
    
    # 清理过期文件
    storage.cleanup_old_files()
    print("已清理过期文件")
    
    # 输出结果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    else:
        # 输出到stdout（供OpenClaw使用）
        print(json.dumps(daily_data, ensure_ascii=False))

def run_weekly_analysis(processor, storage, output_file=None):
    """执行周度分析"""
    print("开始周度分析...")
    
    # 获取最近7天的数据
    weekly_events = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data = storage.load_daily_data(date)
        if daily_data and 'events' in daily_data:
            weekly_events.extend(daily_data['events'])
    
    if not weekly_events:
        print("没有找到足够的数据进行周度分析")
        return
    
    # 执行趋势分析（简化版）
    categories_count = {}
    for event in weekly_events:
        category = event.get('primary_category', 'general')
        categories_count[category] = categories_count.get(category, 0) + 1
    
    # 生成周报
    week_number = datetime.now().strftime('%Y-W%U')
    weekly_report = {
        'week': week_number,
        'date_range': [
            (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        ],
        'total_events': len(weekly_events),
        'category_distribution': categories_count,
        'top_events': sorted(weekly_events, key=lambda x: x['hotness_score'], reverse=True)[:10]
    }
    
    storage.save_weekly_report(week_number, weekly_report)
    print(f"已保存周度报告到 .techhorizon/weekly/{week_number}.json")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(weekly_report, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    else:
        print(json.dumps(weekly_report, ensure_ascii=False))

def run_monthly_analysis(processor, storage, output_file=None):
    """执行月度分析"""
    print("开始月度分析...")
    
    # 获取最近30天的数据
    monthly_events = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data = storage.load_daily_data(date)
        if daily_data and 'events' in daily_data:
            monthly_events.extend(daily_data['events'])
    
    if not monthly_events:
        print("没有找到足够的数据进行月度分析")
        return
    
    # 生成月报
    current_month = datetime.now().strftime('%Y-%m')
    monthly_report = {
        'month': current_month,
        'total_events': len(monthly_events),
        'top_categories': get_top_categories(monthly_events),
        'top_events': sorted(monthly_events, key=lambda x: x['hotness_score'], reverse=True)[:20]
    }
    
    storage.save_monthly_report(current_month, monthly_report)
    print(f"已保存月度报告到 .techhorizon/monthly/{current_month}.json")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(monthly_report, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    else:
        print(json.dumps(monthly_report, ensure_ascii=False))

def get_top_categories(events):
    """获取热门分类"""
    categories = {}
    for event in events:
        category = event.get('primary_category', 'general')
        categories[category] = categories.get(category, 0) + 1
    
    return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])

if __name__ == "__main__":
    main()