# TechHorizon - IT/编程/科技技术界情报收集分析

全面监控 IT/编程/科技技术界的重大热门事件，提供多层级趋势分析。

## 功能特性

- **多数据源覆盖**: GitHub Trending、Hacker News、ReadHub、开源中国、掘金等
- **中英双语处理**: 标题显示"中文（原英文）"，描述自动翻译为中文
- **智能分类**: 按技术领域、事件类型自动分类
- **多层级分析**: 日/周/月/年四层级趋势分析
- **通用数据输出**: 生成结构化JSON数据，可被任何消息渠道使用

## 数据源配置

- GitHub Trending (25条/天)
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

## 输出格式

Skill通过标准输出(stdout)返回结构化JSON数据，包含：
- 原始事件数据（每日模式）
- 趋势分析报告（周度/月度模式）
- 分类统计信息
- 热度评分排序

调用方可以根据需要将数据发送到任何支持的消息渠道（webchat, telegram, whatsapp, discord, signal, dingtalk, qqbot, wecom, feishu等）。

## 技术实现

- 使用真实API和网页解析获取数据
- 支持所有配置的数据源
- 自动处理中英文内容
- 包含错误处理和重试机制
- 遵循各网站的robots.txt和使用条款