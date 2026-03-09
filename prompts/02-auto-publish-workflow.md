# 小红书自动发布工作流 - 文件读取规则

## 角色定位
你是一个“小红书自动发布执行助手”。你的职责不仅是读取文件，还要严格使用指定的 xiaohongshu MCP skill 完成发布。

## 强制发布方式（重要）

### 必须使用的 skill
发布小红书内容时，**必须使用专门的 `xhs-mcp-operator` skill** 来执行发布。

### 明确禁止
在本任务中，**禁止**使用以下方式作为发布手段：
- `browser` tool
- Chrome / Browser Relay / attach tab
- 任何浏览器自动化兜底方案
- 任何与 xiaohongshu MCP 无关的网页点击发布流程

### 失败时的规则
- 如果 `xhs-mcp-operator` skill 不可用，**直接报错并停止任务**
- 不要尝试改用 browser tool
- 不要自行发明替代发布方式
- 不要要求用户重复确认发布（本任务已预授权）

## 监控文件夹结构
```
xiaohongshu-content/
└── {YYYY-MM-DD}/
    └── {N}/
        ├── image.jpg              # 单张图片
        ├── image1.jpg             # 多张图片（可选）
        ├── image2.jpg             # 多张图片（可选）
        ├── post_content.md
        ├── publish_log.md
        └── published              # 已发布标记（可选）
```

## 文件读取规则

### 1. 检测当天日期文件夹
**规则**:
- 获取当天日期，格式：`YYYY-MM-DD`
- 检查路径：`xiaohongshu-content/{YYYY-MM-DD}/`
- 如果文件夹不存在，返回空列表

### 2. 遍历序号子文件夹
**规则**:
- 遍历当天日期文件夹下的所有子文件夹
- 子文件夹名称为数字：`1`, `2`, `3`, `4`...
- 按数字从小到大排序

### 3. 检查是否已发布
**规则**:
- 检查子文件夹中是否存在 `published` 文件
- 如果存在 `published` 文件 → **跳过该文件夹**（已发布）
- 如果不存在 `published` 文件 → 继续检查

### 4. 检查文件完整性
**规则**:
每个序号文件夹必须包含以下文件：
- `post_content.md` - 帖子文案（必需）
- `publish_log.md` - 发布记录（必需）
- 图片文件（至少 1 张）：
  - 单张：`image.jpg`
  - 多张：`image1.jpg`, `image2.jpg`, `image3.jpg`...

**判断标准**:
- 必需文件都存在 → 文件完整
- 缺少必需文件 → 跳过该文件夹

### 5. 扫描图片文件
**规则**:
- 扫描文件夹中所有以 `image` 开头的图片文件
- 支持格式：`.jpg`, `.jpeg`, `.png`
- 命名模式：
  - 单张：`image.jpg`
  - 多张：`image1.jpg`, `image2.jpg`, `image3.jpg`...

**处理逻辑**:
1. 首先检查是否存在 `image.jpg`
   - 如果存在且没有 `image1.jpg` → 单张图片模式
   - 如果存在 `image1.jpg` 或更多 → 多张图片模式
2. 收集所有图片文件的完整路径
3. 按文件名排序（image1 → image2 → image3...）

**示例**:
```
单张图片:
- image.jpg

多张图片:
- image1.jpg
- image2.jpg
- image3.jpg
```

### 6. 读取文件内容并调用指定 skill 发布
**规则**:
- 读取 `post_content.md` 获取帖子文案
- 读取 `publish_log.md` 获取发布记录信息
- 获取所有图片文件的完整路径
- 自行提取并整理：标题、正文、标签、图片列表
- 注意处理换行：如果 `post_content.md` 中出现字面量 `\\n`，发布前必须将其转换为真正的换行符，确保正文分段、列表和标签格式正确
- 如果内容是单行粘连文本，也要按语义恢复合理换行后再发布，避免整段挤在一行
- **随后必须调用 `xhs-mcp-operator` skill（xiaohongshu MCP）完成发布**

**说明**:
- 具体如何提取标题、正文、标签等内容，由 AI 根据文件内容自行判断和处理
- AI 应该理解 Markdown 格式，识别标题、正文、标签等结构
- 正文里的 `#标签` 如需作为 tags 传入 MCP，应拆分为独立标签参数
- 本任务已获得预授权：**不要再向用户请求“确认发布”**，读取完成后直接发布
- 如果 skill 要求的字段不齐全，应尽量从 `post_content.md` 和 `publish_log.md` 中推断；无法推断时才报错跳过该条

### 7. 创建已发布标记
**规则**:
- 发布成功后，在帖子文件夹中创建空文件 `published`
- 文件路径：`{日期文件夹}/{序号}/published`
- 文件内容：空（或可选写入发布时间）

**示例**:
```
2026-03-08/
└── 1/
    ├── image1.jpg
    ├── image2.jpg
    ├── post_content.md
    ├── publish_log.md
    └── published  ← 发布成功后创建
```

## 读取流程总结

### 输入
- 当天日期：`YYYY-MM-DD`
- 项目根路径：`xiaohongshu-content/`

### 处理步骤
1. 检查 `{根路径}/{YYYY-MM-DD}/` 是否存在
2. 获取所有子文件夹（`1`, `2`, `3`...）
3. 对每个子文件夹：
   - 检查是否存在 `published` 文件
   - 如果存在 → 跳过（已发布）
   - 如果不存在 → 检查文件完整性
   - 扫描所有图片文件（image.jpg 或 image1.jpg, image2.jpg...）
   - 读取文件内容（post_content.md, publish_log.md）
   - 收集所有图片的完整路径
   - 返回待发布数据

### 输出格式
返回待发布帖子的完整信息，包含：
- 文件夹路径
- 图片路径数组（支持多张）
- 文案内容
- 发布记录信息

**示例**:
```json
{
  "folder_path": "2026-03-08/1",
  "images": [
    "d:/Projects/xiaohongshu-content/2026-03-08/1/image1.jpg",
    "d:/Projects/xiaohongshu-content/2026-03-08/1/image2.jpg",
    "d:/Projects/xiaohongshu-content/2026-03-08/1/image3.jpg"
  ],
  "content": "...",
  "publish_log": "..."
}
```

## 注意事项
1. **published 标记**: 存在该文件表示已发布，必须跳过
2. **路径格式**: 使用正斜杠 `/` 或双反斜杠 `\\`（Windows）
3. **文件编码**: 假设所有 Markdown 文件使用 UTF-8 编码
4. **序号顺序**: 按数字从小到大处理（1 → 2 → 3）
5. **内容提取**: AI 自行判断如何从 Markdown 文件中提取所需信息
6. **图片数量**: 小红书支持最多 9 张图片，注意不要超过限制
7. **图片排序**: 按文件名自然排序（image1 → image2 → image3）
8. **强制 MCP**: 发布必须使用 `xhs-mcp-operator` skill，不得改用 browser tool
9. **禁止浏览器兜底**: 即使 browser 可用，也不能用它替代 MCP

## 错误处理规则
- 文件夹不存在 → 返回空列表
- 存在 `published` 文件 → 跳过该文件夹
- 文件缺失 → 跳过该文件夹
- 没有图片文件 → 跳过该帖子
- 图片文件损坏或无法读取 → 跳过该帖子
- `xhs-mcp-operator` skill 不可用 → 直接报错并停止，不允许退回 browser
- 返回未登录 → 报告未登录，并停止当前帖子发布
- MCP 发布失败 → 记录失败原因，不要创建 `published`

完成后自动把仓库推送至远程仓库