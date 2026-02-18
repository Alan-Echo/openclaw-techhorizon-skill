# TechHorizon - IT/编程/科技技术界情报收集分析

全面监控 IT/编程/科技技术界的重大热门事件，提供多层级趋势分析。

## 功能特性

- **多数据源覆盖**: GitHub/Gitee Trending、Hacker News、ReadHub、开源中国、掘金等
- **中英双语处理**: 标题显示"中文（原英文）"，描述自动翻译为中文
- **智能分类**: 按技术领域、事件类型自动分类
- **多层级分析**: 日/周/月/年四层级趋势分析
- **企业微信推送**: 定时通过企业微信发送分析报告

## 数据源配置

- GitHub Trending (25条/天)
- Gitee Trending (25条/天)  
- Hacker News (30条/天)
- ReadHub (20条/天)
- 开源中国 (15条/天)
- 掘金 (15条/天)
- 安全漏洞源 (CNVD + GitHub Security, ≤20条/天)
- 大厂技术博客 (≤10条/天)

## 文件存储

- `.techhorizon/daily/` - 30天保留
- `.techhorizon/weekly/` - 52周保留  
- `.techhorizon/monthly/` - 24个月保留
- `.techhorizon/cache/` - 7天保留

## 使用方法

在 cron job 中调用：
```
运行 TechHorizon Skill，收集 IT/编程/科技界重大热门事件
```

支持的指令：
- "收集今日科技热点"
- "生成周度趋势分析"  
- "生成月度深度报告"
- "查看安全漏洞警报"