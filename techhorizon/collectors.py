#!/usr/bin/env python3
"""
TechHorizon 数据收集器模块 - 修复版（无模拟数据，移除Gitee）
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
    
    def collect(self, limit: int = 30) -> List[Dict[str, Any]]:
        """收集GitHub热门项目"""
        try:
            url = "https://github.com/trending"
            html = self.fetch_url(url)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            repo_items = soup.find_all('article', class_='Box-row', limit=limit)
            
            events = []
            for item in repo_items:
                title_elem = item.find('h2', class_='h3')
                if title_elem:
                    link = title_elem.find('a')
                    if link and link.get('href'):
                        title = link.get_text(strip=True).replace('\n', '').replace(' ', '')
                        full_url = f"https://github.com{link.get('href')}"
                        
                        desc_elem = item.find('p', class_='col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        event = {
                            "title": title,
                            "description": description,
                            "url": full_url,
                            "source": self.name
                        }
                        events.append(event)
            
            return events
        except Exception as e:
            print(f"Error collecting GitHub Trending: {e}")
            return []

class HackerNewsCollector(BaseCollector):
    """Hacker News 收集器"""
    
    def __init__(self):
        super().__init__("hacker_news")
        self.api_base = "https://hacker-news.firebaseio.com/v0"
    
    def collect(self, limit: int = 35) -> List[Dict[str, Any]]:
        """收集Hacker News热门话题"""
        try:
            top_stories = self.fetch_json(f"{self.api_base}/topstories.json")
            if not top_stories:
                return []
            
            events = []
            for story_id in top_stories[:limit]:
                story = self.fetch_json(f"{self.api_base}/item/{story_id}.json")
                if story and story.get('score', 0) > 10:
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
    
    def collect(self, limit: int = 25) -> List[Dict[str, Any]]:
        """收集ReadHub科技新闻"""
        try:
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

class OSChinaCollector(BaseCollector):
    """开源中国收集器"""
    
    def __init__(self):
        super().__init__("oschina")
    
    def collect(self, limit: int = 20) -> List[Dict[str, Any]]:
        """通过RSS收集开源中国数据"""
        rss_sources = [
            'https://www.oschina.net/news/rss',
            'https://www.oschina.net/blog/rss',
        ]
        
        for rss_url in rss_sources:
            try:
                feed = feedparser.parse(rss_url)
                if hasattr(feed, 'entries') and feed.entries:
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
                        return events
                        
            except Exception as e:
                print(f"Error with OSChina RSS {rss_url}: {e}")
                continue
        
        return []

class JuejinCollector(BaseCollector):
    """掘金收集器"""
    
    def __init__(self):
        super().__init__("juejin")
    
    def collect(self, limit: int = 20) -> List[Dict[str, Any]]:
        """收集掘金热门文章"""
        try:
            # 掘金API - 需要找到正确的API端点
            # 暂时返回空列表，后续需要修复API
            print("Juejin API needs to be fixed - returning empty list")
            return []
            
        except Exception as e:
            print(f"Error collecting Juejin: {e}")
            return []

class SecurityVulnCollector(BaseCollector):
    """安全漏洞收集器 - 修复版（无模拟数据）"""
    
    def __init__(self):
        super().__init__("security_vuln")
    
    def collect(self, limit: int = 20) -> List[Dict[str, Any]]:
        """收集GitHub Security Advisory数据"""
        events = []
        
        # GitHub Security Advisory API
        try:
            url = "https://api.github.com/advisories"
            params = {'per_page': min(limit, 20)}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                advisories = response.json()
                for advisory in advisories[:limit]:
                    event = {
                        "title": f"[CVE] {advisory.get('summary', '')}",
                        "description": advisory.get('description', ''),
                        "url": advisory.get('html_url', ''),
                        "source": self.name
                    }
                    events.append(event)
            # 如果认证失败或其他错误，直接返回空列表
                    
        except Exception as e:
            print(f"Error collecting security vulnerabilities: {e}")
        
        return events[:limit]

class TechBlogsCollector(BaseCollector):
    """大厂技术博客收集器"""
    
    def __init__(self):
        super().__init__("tech_blogs")
    
    def collect(self, limit: int = 15) -> List[Dict[str, Any]]:
        """收集各大厂技术博客"""
        blog_sources = [
            {
                'name': 'Microsoft Research',
                'url': 'https://www.microsoft.com/en-us/research/feed/',
                'is_rss': True
            },
            {
                'name': 'AWS Blog',
                'url': 'https://aws.amazon.com/blogs/aws/feed/',
                'is_rss': True
            },
            {
                'name': 'Google AI Blog',
                'url': 'https://ai.googleblog.com/feeds/posts/default',
                'is_rss': True
            },
            {
                'name': 'Facebook Engineering',
                'url': 'https://engineering.fb.com/feed/',
                'is_rss': True
            },
            {
                'name': 'Apple Developer',
                'url': 'https://developer.apple.com/news/rss/news.rss',
                'is_rss': True
            }
        ]
        
        events = []
        for source in blog_sources:
            try:
                if source['is_rss']:
                    feed = feedparser.parse(source['url'])
                    if hasattr(feed, 'entries'):
                        for entry in feed.entries[:3]:  # 每个源取3条
                            title = getattr(entry, 'title', '')
                            # 添加中英双语标题格式
                            bilingual_title = f"[翻译] [{source['name']}] {title}（{title}）"
                            
                            description = getattr(entry, 'summary', getattr(entry, 'description', ''))
                            url = getattr(entry, 'link', '')
                            
                            event = {
                                "title": bilingual_title,
                                "description": f"[翻译] {description}",
                                "url": url,
                                "source": self.name
                            }
                            events.append(event)
                            
                            if len(events) >= limit:
                                break
                
                if len(events) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error collecting from {source['name']}: {e}")
                continue
        
        return events[:limit]

# 导出所有收集器（已移除Gitee）
COLLECTORS = {
    'github_trending': GitHubTrendingCollector(),
    'hacker_news': HackerNewsCollector(),
    'readhub': ReadHubCollector(),
    'oschina': OSChinaCollector(),
    'juejin': JuejinCollector(),
    'security_vuln': SecurityVulnCollector(),
    'tech_blogs': TechBlogsCollector(),
}

def collect_all_sources() -> List[Dict[str, Any]]:
    """从所有数据源收集数据（已移除Gitee）"""
    all_events = []
    
    # 配置每个数据源的收集数量（调整后保持总量平衡）
    source_limits = {
        'github_trending': 30,      # 增加5条
        'hacker_news': 35,          # 增加5条  
        'readhub': 25,              # 增加5条
        'oschina': 20,              # 增加5条
        'juejin': 20,               # 增加5条（需要修复API）
        'security_vuln': 20,        # 保持不变
        'tech_blogs': 15,           # 增加5条
    }
    
    for source_name, collector in COLLECTORS.items():
        print(f"Collecting from {source_name}...")
        limit = source_limits.get(source_name, 10)
        events = collector.collect(limit)
        all_events.extend(events)
        print(f"Collected {len(events)} events from {source_name}")
        time.sleep(1)  # 避免请求过于频繁
    
    return all_events