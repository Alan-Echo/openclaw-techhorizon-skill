# TechHorizon Skill

IT/编程/科技技术界情报收集分析工具

## 功能特性

- **多数据源覆盖**: GitHub/Gitee Trending、Hacker News、ReadHub、开源中国、掘金等
- **中英双语处理**: 标题显示"中文（原英文）"，描述自动翻译为中文  
- **智能分类**: 按技术领域、事件类型自动分类
- **多层级分析**: 日/周/月/年四层级趋势分析
- **企业微信推送**: 定时通过企业微信发送分析报告

## 安装和使用

### 1. 技能目录结构
```
skills/techhorizon/
├── SKILL.md              # 技能说明文件
├── pyproject.toml        # 依赖配置
├── README.md            # 使用说明
├── scripts/             # 核心代码
│   ├── __init__.py
│   ├── collectors.py    # 数据收集器
│   ├── processor.py     # 数据处理器  
│   ├── storage.py       # 文件存储
│   └── main.py          # 主执行脚本
└── test_skill.py        # 测试脚本
```

### 2. 在 OpenClaw 中使用

在 cron job 中调用：
```
运行 TechHorizon Skill，收集 IT/编程/科技界重大热门事件
```

### 3. 命令行使用

```bash
# 每日数据收集
cd skills/techhorizon
python scripts/main.py --mode daily

# 周度分析  
python scripts/main.py --mode weekly

# 月度分析
python scripts/main.py --mode monthly
```

## 数据存储

所有数据存储在 `.techhorizon/` 目录下：
- `daily/` - 每日原始数据 (保留30天)
- `weekly/` - 周度分析报告 (保留52周)  
- `monthly/` - 月度分析报告 (保留24个月)
- `cache/` - 缓存数据 (保留7天)

## 配置说明

- **总存储需求**: ~9.4MB
- **内存需求**: ~4MB峰值
- **支持的数据源**: 8个主要数据源
- **每日事件数量**: 80-100条高质量事件

## 注意事项

1. **翻译功能**: 当前使用模拟翻译，实际部署时需要集成真实翻译API
2. **GitHub/Gitee爬虫**: 需要实现HTML解析或使用官方API
3. **网络依赖**: 需要稳定的网络连接访问各数据源
4. **资源友好**: 在40G磁盘+2G内存环境下完全适用

## 扩展性

- 易于添加新的数据源
- 支持自定义分类规则  
- 可配置保留策略
- 模块化设计便于维护