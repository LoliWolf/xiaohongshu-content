# Bing 每日壁纸 → 小红书内容 工作流

## 目标
每天北京时间 00:00 获取 Bing 中国区每日壁纸，并基于：
- `title`
- `copyright`
- 图片本身

理解当日壁纸主题，然后按 `prompts/01-content-generation.md` 的规则，在当天目录下创建新的内容文件夹。

## 本地工作流入口
```bash
/Users/loli_wolf/.openclaw/workspace/scripts/run_bing_xhs_workflow.sh
```

## 产出位置
```text
xiaohongshu-content/
└── YYYY-MM-DD/
    └── N/
        ├── image.jpg
        ├── post_content.md
        └── publish_log.md
```

## 规则说明
- 日期目录使用**执行当天北京时间**，不是 Bing API 的 `startdate`
- 序号目录自动递增：`1/ 2/ 3/ ...`
- 图片保存为 `image.jpg`
- 文案根据 `prompts/01-content-generation.md` 生成

## 依赖来源
- Bing skill 参考：`/Users/loli_wolf/.openclaw/skills/bing-daily-wallpaper/`
- 核心脚本：`/Users/loli_wolf/.openclaw/workspace/scripts/bing_to_xiaohongshu.py`
