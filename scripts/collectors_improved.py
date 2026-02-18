#!/usr/bin/env python3
"""
TechHorizon 改进版数据收集器模块
修复Gitee和OSChina的反爬虫问题
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import feedparser

class BaseCollector:
    """数据收集器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        # 使用更真实的浏览器User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
    
    def fetch_json(self, url: str, timeout: int = 10, **kwargs) -> Dict:
        """获取JSON数据"""
        try:
            response = self.session.get(url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching JSON from {url}: {e}")
            return {}

class GiteeTrendingCollector(BaseCollector):
    """Gitee Trending 收集器 - 使用官方API"""
    
    def __init__(self):
        super().__init__("gitee_trending")
    
    def collect(self, limit: int = 25) -> List[Dict[str, Any]]:
        """使用Gitee官方API收集热门项目"""
        try:
            events = []
            page = 1
            per_page = min(limit, 25)  # Gitee API每页最多25条
            
            # 使用Gitee官方API
            url = "https://gitee.com/api/v5/repositories"
            params = {
                'sort': 'popular',
                'order': 'desc',
                'per_page': per_page,
                'page': page
            }
            
            repos = self.fetch_json(url, params=params)
            if not repos:
                print(f"No data returned from Gitee API")
                return []
            
            for repo in repos[:limit]:
                if isinstance(repo, dict):
                    event = {
                        "title": repo.get('name', ''),
                        "description": repo.get('description', ''),
                        "url": repo.get('html_url', ''),
                        "source": self.name
                    }
                    events.append(event)
            
            print(f"Collected {len(events)} events from Gitee API")
            return events
            
        except Exception as e:
            print(f"Error collecting from Gitee API: {e}")
            return []

class OSCollector(BaseCollector):
    """开源中国收集器 - 使用备用方案"""
    
    def __init__(self):
        super().__init__("oschina")
    
    def collect(self, limit: int = 15) -> List[Dict[str, Any]]:
        """尝试多种方式收集开源中国数据"""
        # 方案1: 尝试不同的RSS源
        rss_sources = [
            'https://www.oschina.net/news/rss',
            'https://www.oschina.net/blog/rss',  # 博客RSS
        ]
        
        for rss_url in rss_sources:
            try:
                print(f"Trying OSChina RSS: {rss_url}")
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    events = []
                    for entry in feed.entries[:limit]:
                        event = {
                            "title": getattr(entry, 'title', ''),
                            "description": getattr(entry, 'summary', getattr(entry, 'description', '')),
                            "url": getattr(entry, 'link', ''),
                            "source": self.name
                        }
                        events.append(event)
                    
                    if events:
                        print(f"Collected {len(events)} events from OSChina RSS")
                        return events
                        
            except Exception as e:
                print(f"Error with OSChina RSS {rss_url}: {e}")
                continue
        
        # 方案2: 尝试直接网页抓取（带更好的headers）
        try:
            print("Trying OSChina web scraping...")
            html = self.fetch_url("https://www.oschina.net/news")
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # 查找新闻列表（需要根据实际页面结构调整选择器）
                news_items = soup.find_all(['h3', 'h2', '.news-item', '.title'], limit=limit)
                events = []
                for item in news_items:
                    title_elem = item.find('a') if item.name != 'a' else item
                    if title_elem and title_elem.get('href'):
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href')
                        if not url.startswith('http'):
                            url = 'https://www.oschina.net' + url
                        event = {
                            "title": title,
                            "description": "",
                            "url": url,
                            "source": self.name
                        }
                        events.append(event)
                
                if events:
                    print(f"Collected {len(events)} events from OSChina web scraping")
                    return events
                    
        except Exception as e:
            print(f"Error with OSChina web scraping: {e}")
        
        # 方案3: 使用备选中文技术社区
        print("Using backup Chinese tech sources...")
        return self.collect_backup_sources(limit)
    
    def collect_backup_sources(self, limit: int) -> List[Dict[str, Any]]:
        """使用备选中文技术社区"""
        events = []
        
        # 尝试V2EX中文区
        try:
            v2ex_url = "https://www.v2ex.com/api/topics/latest.json"
            topics = self.fetch_json(v2ex_url)
            if topics and isinstance(topics, list):
                for topic in topics[:min(limit//2, 10)]:
                    if isinstance(topic, dict) and 'title' in topic:
                        event = {
                            "title": topic.get('title', ''),
                            "description": "",
                            "url": f"https://www.v2ex.com/t/{topic.get('id', '')}",
                            "source": "v2ex_backup"
                        }
                        events.append(event)
        except Exception as e:
            print(f"Error with V2EX backup: {e}")
        
        # 尝试SegmentFault
        try:
            sf_url = "https://segmentfault.com/api/blogs?tab=hot"
            blogs = self.fetch_json(sf_url)
            if blogs and isinstance(blogs, dict) and 'data' in blogs:
                for blog in blogs['data'][:min(limit//2, 10)]:
                    if isinstance(blog, dict):
                        event = {
                            "title": blog.get('title', ''),
                            "description": blog.get('excerpt', ''),
                            "url": f"https://segmentfault.com{blog.get('url', '')}",
                            "source": "segmentfault_backup"
                        }
                        events.append(event)
        except Exception as e:
            print(f"Error with SegmentFault backup: {e}")
        
        return events[:limit]

# 其他收集器保持不变...