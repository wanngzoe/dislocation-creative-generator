# Prompt 方案 v1（旧版）

## 目录
1. [方向提取 Prompt](#方向提取-prompt)
2. [文案生成 Prompt](#文案生成-prompt)
3. [故事总结 Prompt](#故事总结-prompt)
4. [使用说明](#使用说明)

---

## 方向提取 Prompt

### get_direction_prompt_v1

```python
def get_direction_prompt_v1(subtitle_text):
    return f"""你是一个顶级的爆款故事拆解专家。你的任务是分析输入的故事大纲或文本，提取用于创作极具视觉冲击力与信息缺口的核心要素

## 内容
{subtitle_text}

## 输出要求（严格JSON数组）
[{{
    "主人公": "第一人称主人公身份（如：被卖的小女孩、新婚儿媳、太子、丫鬟等）",
    "核心冲突": "一句话描述最抓人眼球的核心冲突（如：至亲背叛、身份错位、求助者正是伤害她的人）",
    "意象词": ["广告文案可直接使用的具体物品/场景词，如：馒头、镯子、卖身契、骨头汤等"],
    "情绪基调": "整体情绪氛围（如：绝望、讽刺、悲凉、愤怒）",
    "可用要素": "可用于创作的关键元素提取"
}}]

## 提取原则
1. 只输出JSON数组
2. 主人公要明确（如：小女孩、儿媳、太子）
3. 意象词要具体名词，可用逗号分隔
4. 核心冲突要一句话描述核心冲突，不描述过程细节
5. 核心冲突和可用要素中，使用具体的、有画面感的动作词（如：焚烧、凌迟、沸煮），避免只用抽象词（如：惨烈、痛苦）
6. 如有敏感意象，可用标点符号分隔或用近义词替代

重要：只输出JSON数组，不要任何其他内容！"""
```

**特点**：
- 输出为 JSON 数组（包含单个对象的数组）
- 相对宽松的限制
- 核心冲突描述较灵活

---

## 文案生成 Prompt

### get_plot_twist_prompt_v1 (合并版)

```python
def get_plot_twist_prompt_v1(story_material, count, word_count, requirements, mode="product"):
    return f"""你是一个拥有千万粉丝的首席爆款文案师。你的任务是根据以下故事素材，写{count}条极具吸引力的短文案（Hook）。

要求：
- 黄金3秒开篇
- 画面感强，反转冲击力大，刀刀致命
- 主人公第一人称视角
- 不要输出任何语气标签、括号注释
- 描述事件时使用动作化表达，避免心理描写和流水账叙述

故事素材：
{story_material}

格式要求：
- 每条{word_count}字
- 直接可用，不要解释

附加要求：
{requirements}

输出JSON数组：
[
  {{
    "copy": "文案",
    "conflict_angle": "冲突角度",
    "relationship": "关系视角"
  }}
]

重要：只输出JSON数组！"""
```

**合并后的特点**：
- 角色设定：首席爆款文案师（来自原提示词方案）
- 输出字段：copy + conflict_angle + relationship（来自原提示词方案）
- 动作化要求：避免心理描写和流水账叙述（来自原产品方案）
- mode 参数保留但效果相同（不再区分 product/prompt）

---

## 故事总结 Prompt

### get_summary_prompt（方案2）

```python
def get_summary_prompt(subtitle_text):
    return f"""分析以下短剧字幕，提取可用于广告文案的具体要素。

## 字幕内容
{subtitle_text}

## 输出要求（严格JSON数组）
[{{
    "视角人物": "第一人称视角人物（如：小女孩）",
    "关系网": "人物关系及身份（如：爹-屠夫残忍，娘-被卖受害者，舅舅-冷血见死不救）",
    "核心意象": ["广告文案可直接使用的具体物品/场景词：馒头、镯子、卖身契、饥饿、眼泪等"],
    "核心冲突": "最抓人眼球的核心冲突事件（如：亲人反目、身世揭秘、身份错位等）",
    "情绪关键词": ["可用情绪词：绝望、讽刺、悲凉、愤怒等"],
    "反转线索": "故事最大反转（如：求助者正是伤害她的人）"
}}]

## 提取原则
1. 只输出JSON数组
2. 核心意象要具体名词，可用逗号分隔（如：馒头,镯子,骨头汤）
3. 核心冲突要一句话描述核心冲突，不描述过程细节
4. 如有敏感意象，可用标点符号分隔或用近义词替代

重要：只输出JSON数组，不要任何其他内容！"""
```

**特点**：
- 相比方案1更完整的分析
- 包含关系网、反转线索等
- 适合复杂故事

---

## 使用说明

### 在 app.py 中的位置
- `get_direction_prompt_v1()` - 第 140 行
- `get_plot_twist_prompt_v1()` - 第 164 行
- `get_summary_prompt()` - 第 248 行

### 调用方式
```python
# 通过统一接口调用
prompt = get_direction_prompt(subtitle_text)  # 自动选择 v1 或 v2
prompt = get_plot_twist_prompt(story_material, count, word_count, requirements, mode)

# 直接调用 v1
prompt = get_direction_prompt_v1(subtitle_text)
prompt = get_plot_twist_prompt_v1(story_material, count, word_count, requirements, mode)
```

### 版本切换
在 Streamlit UI 中，用户可以通过 "Prompt版本" 单选按钮选择 v1 或 v2。

---

## v1 vs v2 对比

| 方面 | v1（旧版） | v2（新版） |
|------|-----------|-----------|
| **方向提取** | | |
| 输出格式 | JSON数组 `[{}]` | JSON对象 `{}` |
| 字段名 | 主人公、核心冲突、意象词等 | anchor_symbol、core_conflict、image_words 等 |
| 约束 | 较宽松 | 严格（符号锚点、冲突限定） |
| **文案生成** | | |
| 禁止项 | 无明确禁止 | 5条绝对禁止项 |
| 标点约束 | 无 | 2-3个逗号 |
| 爆点约束 | 无 | 结尾5字爆点 |
| 框架类型 | 无 | 4大框架类型 |
| 风格 | 相对宽松自然 | 限制严格 |

---

## 修改后同步到 app.py

修改完本文档后，需要将对应的 prompt 函数代码复制到 `app.py` 中替换原有函数。
