#!/usr/bin/env python3
"""
TechHorizon 数据处理器模块
负责数据翻译、分类、去重等处理
"""

import json
import re
from typing import List, Dict, Any
from datetime import datetime

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        # 技术领域关键词
        self.tech_categories = {
            'ai_ml': ['AI', '机器学习', '深度学习', '大模型', 'LLM', 'neural network', 'artificial intelligence'],
            'security': ['安全', '漏洞', 'CVE', 'exploit', 'security', 'vulnerability', 'hack'],
            'web_dev': ['Web开发', 'JavaScript', 'React', 'Vue', 'frontend', 'backend', 'web'],
            'systems': ['系统编程', 'Rust', 'Go', 'C++', 'performance', 'low-level', 'system'],
            'cloud': ['云计算', 'AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker', 'cloud'],
            'blockchain': ['区块链', 'Web3', 'crypto', 'ethereum', '智能合约', 'blockchain'],
            'mobile': ['移动开发', 'iOS', 'Android', 'Flutter', 'React Native', 'mobile'],
            'database': ['数据库', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'database'],
            'devops': ['DevOps', 'CI/CD', 'GitHub Actions', 'Jenkins', 'automation', 'devops'],
            'startup': ['创业', '融资', '收购', 'IPO', 'startup', 'funding', 'investment']
        }
        
        # 事件类型关键词
        self.event_types = {
            'new_release': ['发布', 'release', 'launch', '推出', 'new'],
            'security_alert': ['漏洞', '安全警告', 'security advisory', 'CVE', 'alert'],
            'trending_project': ['热门', 'trending', '热门项目', 'star', 'popular'],
            'major_announcement': ['重大公告', 'announcement', '重大发布', 'major'],
            'funding_news': ['融资', '投资', 'funding', 'acquisition', 'investment'],
            'community_discussion': ['讨论', '社区', 'discussion', 'community', 'talk']
        }
    
    def is_chinese(self, text: str) -> bool:
        """判断文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def translate_to_chinese(self, text: str) -> str:
        """翻译英文为中文（模拟实现）"""
        # TODO: 集成实际的翻译API
        # 这里返回模拟翻译结果
        if not text.strip():
            return "无描述信息"
        
        # 简单的模拟翻译（实际应该调用翻译服务）
        translations = {
            "Sample GitHub Project": "示例GitHub项目",
            "This is a sample GitHub project description": "这是一个示例GitHub项目描述",
            "Hacker News discussion": "Hacker News讨论",
            "Artificial Intelligence": "人工智能",
            "Machine Learning": "机器学习",
            "Security vulnerability": "安全漏洞",
            "New release": "新版本发布"
        }
        
        translated = text
        for en, zh in translations.items():
            translated = translated.replace(en, zh)
        
        return translated if translated != text else f"[翻译] {text}"
    
    def process_title(self, original_title: str) -> str:
        """处理标题：中文（原英文）"""
        if not original_title.strip():
            return "无标题"
        
        if self.is_chinese(original_title):
            return original_title
        else:
            chinese_title = self.translate_to_chinese(original_title)
            return f"{chinese_title}（{original_title}）"
    
    def process_description(self, original_description: str) -> str:
        """处理描述：只保留中文翻译"""
        if not original_description.strip():
            return "无描述信息"
        
        if self.is_chinese(original_description):
            return original_description
        else:
            return self.translate_to_chinese(original_description)
    
    def classify_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """为事件分配分类标签"""
        title = event['title'].lower()
        description = event['description'].lower()
        full_text = title + ' ' + description
        
        categories = []
        event_types = []
        
        # 技术领域分类
        for category, keywords in self.tech_categories.items():
            if any(keyword.lower() in full_text for keyword in keywords):
                categories.append(category)
        
        # 事件类型分类
        for event_type, keywords in self.event_types.items():
            if any(keyword.lower() in full_text for keyword in keywords):
                event_types.append(event_type)
        
        # 默认分类
        if not categories:
            categories = ['general']
        if not event_types:
            event_types = ['community_discussion']
        
        return {
            'categories': categories,
            'event_types': event_types,
            'primary_category': categories[0]
        }
    
    def calculate_hotness_score(self, event: Dict[str, Any]) -> int:
        """计算热度分数"""
        base_score = 0
        
        # 数据源权重
        source_weights = {
            'github_trending': 10,
            'gitee_trending': 8,
            'hacker_news': 12,
            'readhub': 6,
            'oschina': 5,
            'juejin': 5
        }
        base_score += source_weights.get(event['source'], 1)
        
        # 分类权重
        category_weights = {
            'security': 15,
            'ai_ml': 12,
            'major_announcement': 10
        }
        if event.get('primary_category') in category_weights:
            base_score += category_weights[event['primary_category']]
        
        # 事件类型权重
        if 'security_alert' in event.get('event_types', []):
            base_score += 20
        
        return base_score
    
    def process_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理所有事件"""
        processed_events = []
        
        for event in events:
            # 基础验证
            if not event.get('title') or not event.get('url'):
                continue
            
            # 处理标题和描述
            processed_event = {
                'title': self.process_title(event['title']),
                'description': self.process_description(event['description']),
                'url': event['url'],
                'source': event['source']
            }
            
            # 分类
            classification = self.classify_event(processed_event)
            processed_event.update(classification)
            
            # 热度评分
            processed_event['hotness_score'] = self.calculate_hotness_score(processed_event)
            
            processed_events.append(processed_event)
        
        # 按热度排序
        processed_events.sort(key=lambda x: x['hotness_score'], reverse=True)
        
        return processed_events
    
    def remove_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """移除重复事件"""
        seen_urls = set()
        seen_titles = set()
        unique_events = []
        
        for event in events:
            url_hash = hash(event['url'])
            title_hash = hash(event['title'].lower())
            
            if url_hash not in seen_urls and title_hash not in seen_titles:
                unique_events.append(event)
                seen_urls.add(url_hash)
                seen_titles.add(title_hash)
        
        return unique_events