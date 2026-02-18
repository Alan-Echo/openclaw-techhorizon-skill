#!/usr/bin/env python3
"""
TechHorizon 数据收集器模块
负责从各个数据源收集原始数据
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

class BaseCollector:
    """数据收集器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TechHorizon/1.0 (+https://github.com/yourname/techhorizon)'
        })
    
    def fetch_url(self, url: str, timeout: int = 10) -> str:
        """获取URL内容"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def fetch_json(self, url: str, timeout: int = 10) -> Dict:
        """获取JSON数据"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching JSON from {url}: {e}")
            return {}


class GitHubTrendingCollector(BaseCollector):
    """GitHub Trending 收集器"""
    
    def __init__(self):
        super().__init__("github_trending")
    
    def collect(self, limit: int = 25) -> List[Dict[str, Any]]:
        """收集GitHub热门项目"""
        # TODO: 实现GitHub Trending页面解析
        # 这里需要使用浏览器自动化或HTML解析
        events = []
        for i in range(min(limit, 5)):  # 模拟数据
            events.append({
                "title": f"Sample GitHub Project {i+1}",
                "description": f"This is a sample GitHub project description {i+1}",
                "url": f"https://github.com/sample/project{i+1}",
                "source": self.name
            })
        return events


class GiteeTrendingCollector(BaseCollector):
    """Gitee Trending 收集器"""
    
    def __init__(self):
        super().__init__("gitee_trending")
    
    def collect(self, limit: int = 25) -> List[Dict[str, Any]]:
        """收集Gitee热门项目"""
        events = []
        for i in range(min(limit, 5)):  # 模拟数据
            events.append({
                "title": f"示例Gitee项目 {i+1}",
                "description": f"这是一个示例Gitee项目描述 {i+1}",
                "url": f"https://gitee.com/sample/project{i+1}",
                "source": self.name
            })
        return events


class HackerNewsCollector(BaseCollector):
    """Hacker News 收集器"""
    
    def __init__(self):
        super().__init__("hacker_news")
        self.api_base = "https://hacker-news.firebaseio.com/v0"
    
    def collect(self, limit: int = 30) -> List[Dict[str, Any]]:
        """收集Hacker News热门话题"""
        try:
            # 获取前100个热门故事ID
            top_stories = self.fetch_json(f"{self.api_base}/topstories.json")
            if not top_stories:
                return []
            
            events = []
            for story_id in top_stories[:limit]:
                story = self.fetch_json(f"{self.api_base}/item/{story_id}.json")
                if story and story.get('score', 0) > 50:  # 只取高分故事
                    event = {
                        "title": story.get('title', ''),
                        "description": f"Hacker News discussion with {story.get('score', 0)} points and {story.get('descendants', 0)} comments",
                        "url": story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": self.name
                    }
                    events.append(event)
                    if len(events) >= limit:
                        break
            
            return events
        except Exception as e:
            print(f"Error collecting Hacker News: {e}")
            return []


class ReadHubCollector(BaseCollector):
    """ReadHub 收集器"""
    
    def __init__(self):
        super().__init__("readhub")
    
    def collect(self, limit: int = 20) -> List[Dict[str, Any]]:
        """收集ReadHub科技新闻"""
        try:
            # ReadHub API
            news_data = self.fetch_json("https://api.readhub.cn/news")
            if not news_data or 'data' not in news_data:
                return []
            
            events = []
            for news in news_data['data'][:limit]:
                event = {
                    "title": news.get('title', ''),
                    "description": news.get('summary', ''),
                    "url": news.get('url', ''),
                    "source": self.name
                }
                events.append(event)
            
            return events
        except Exception as e:
            print(f"Error collecting ReadHub: {e}")
            return []


# 导出所有收集器
COLLECTORS = {
    'github_trending': GitHubTrendingCollector(),
    'gitee_trending': GiteeTrendingCollector(),
    'hacker_news': HackerNewsCollector(),
    'readhub': ReadHubCollector(),
}

def collect_all_sources() -> List[Dict[str, Any]]:
    """从所有数据源收集数据"""
    all_events = []
    
    # 配置每个数据源的收集数量
    source_limits = {
        'github_trending': 25,
        'gitee_trending': 25,
        'hacker_news': 30,
        'readhub': 20,
    }
    
    for source_name, collector in COLLECTORS.items():
        print(f"Collecting from {source_name}...")
        limit = source_limits.get(source_name, 10)
        events = collector.collect(limit)
        all_events.extend(events)
        print(f"Collected {len(events)} events from {source_name}")
        time.sleep(1)  # 避免请求过于频繁
    
    return all_events