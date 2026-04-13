import streamlit as st
import requests
import json
import re
import os
import time

# 页面配置
st.set_page_config(
    page_title="错位创意生成器",
    page_icon="🎬",
    layout="wide"
)

# 错位类型选项
DISLOCATION_TYPES = [
    "职业错位", "年龄错位", "性别错位", "时代错位", "物种错位",
    "场景错位", "材质/形态错位", "语言/文化错位", "关系错位", "声音/语言错位",
    "身份/阶层错位", "比例/尺度错位", "状态/情绪错位", "季节/温度错位", "风格/艺术错位",
    "虚拟与现实错位", "职业与技能错位", "因果错位", "数字/数据错位", "组合错位"
]

# 目标用户预设
TARGET_USER_PRESETS = [
    "18-25岁女性", "26-35岁男性", "宝爸宝妈", "打工人",
    "大学生", "职场新人", "中老年人", "游戏玩家"
]

# 年代预设
ERA_PRESETS = [
    "70年代", "80年代", "90年代", "00年代", "10年代",
    "民国", "古代", "未来", "不设限"
]

# 核心冲突角度预设
CONFLICT_ANGLES = [
    "至亲背叛", "有能力者冷漠", "后知后觉", "被迫共犯",
    "系统碾压", "身份互换", "时间循环", "记忆错乱",
    "情感操控", "信任崩塌"
]

# 模型配置
MODEL_PRESETS = {
    "gemini-2.5-pro": {
        "name": "Gemini 2.5 Pro",
        "api_key_label": "Google Gemini API Key",
        "api_key_help": "在 Google AI Studio 获取",
        "api_key_url": "https://aistudio.google.com/app/apikey"
    },
    "MiniMax-2.7": {
        "name": "MiniMax 2.7",
        "api_key_label": "MiniMax API Key",
        "api_key_help": "在 MiniMax开放平台获取",
        "api_key_url": "https://www.minimax.chat/"
    },
    "doubao": {
        "name": "Doubao Seed 2.0 (豆包)",
        "api_key_label": "火山引擎 ARK API Key",
        "api_key_help": "在火山引擎 ARK 获取",
        "api_key_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apikey"
    },
    "qwen": {
        "name": "Qwen (通义千问)",
        "api_key_label": "阿里云 API Key",
        "api_key_help": "在阿里云百炼获取",
        "api_key_url": "https://bailian.console.aliyun.com/"
    }
}

def get_prompt(input_data):
    target_user = input_data["targetUser"]
    dislocation_type = input_data["dislocationType"]
    era = input_data.get("era", "不设限")
    material = input_data.get("material", "")
    reference = input_data.get("reference", "")
    count = input_data["count"]

    if material:
        # 用户填写了素材，生成"钩子+过渡+素材"结构
        return f"""生成恰好{count}条短剧广告引流素材创意。

## 要求
- 目标受众：{target_user}
- 错位类型：{dislocation_type}
- 年代：{era}
- 素材：{material}

## 输出格式（严格JSON，不要其他内容）
[
  {{
    "hookScene": "钩子画面描述（50-80字）",
    "hookNarration": "钩子旁白（10-20字）",
    "transition": "过渡（5-10字）",
    "materialNarration": "素材旁白（直接使用：{material}）"
  }}
]

重要：只输出JSON数组，前面不要有任何文字！"""
    else:
        # 用户没有填写素材，自由发挥生成创意
        return f"""生成恰好{count}条短剧广告引流素材创意。

## 要求
- 目标受众：{target_user}
- 错位类型：{dislocation_type}
- 年代：{era}

## 输出格式（严格JSON，不要其他内容）
[
  {{
    "hookScene": "钩子画面描述（50-80字）",
    "hookNarration": "钩子旁白（10-20字）"
  }}
]

重要：只输出JSON数组，前面不要有任何文字！"""

def get_direction_prompt(subtitle_text):
    return f"""分析以下内容，提取用于广告文案创作的方向要素。

## 内容
{subtitle_text}

## 输出要求（严格JSON数组）
[{{
    "核心冲突": "一句话描述最抓人眼球的核心冲突（如：至亲背叛、身份错位、求助者正是伤害她的人）",
    "意象词": ["广告文案可直接使用的具体物品/场景词，如：馒头、镯子、卖身契、骨头汤等"],
    "情绪基调": "整体情绪氛围（如：绝望、讽刺、悲凉、愤怒）",
    "可用要素": "可用于创作的关键元素提取"
}}]

## 提取原则
1. 只输出JSON数组
2. 意象词要具体名词，可用逗号分隔
3. 核心冲突要一句话描述核心冲突，不描述过程细节
4. 如有敏感意象，可用标点符号分隔或用近义词替代

重要：只输出JSON数组，不要任何其他内容！"""

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

def get_plot_twist_prompt(story_material, count, duration, requirements):
    return f"""根据以下故事要素，写{count}条短视频配音文案。

## 故事要素
{story_material}

## 核心原则
**画面感 + 反转冲击力 + 想点击（爽、猎奇、等）**

## 创作方法
1. **画面感**：每句话要有极强的画面感和反转冲击力，刀刀致命。直接可用（如：凌晨四点的厨房、婆婆的大脸、500万）
2. **语气有反差**：根据故事要素中的设定，选取最有冲击或反差的语气叙述（如：小女孩：稚嫩又刺骨，儿媳：淡定又爽感）

## 格式要求
- 每条{duration}（10秒约20字，30秒约100字，60秒约200字）
- 直接可用，不要解释

## 附加要求
{requirements}

## 输出格式（严格JSON）
[
  {{
    "copy": "文案（画面感+反转+吸引人点击）",
    "conflict_angle": "冲突类型",
    "relationship": "关系视角"
  }}
]

重要：只输出JSON数组！"""

def call_api(model, api_key, prompt):
    """统一API调用函数，根据模型选择不同的端点和格式"""

    if model == "gemini-2.5-pro":
        return call_gemini(api_key, prompt)
    elif model == "MiniMax-2.7":
        return call_minimax(api_key, prompt)
    elif model == "doubao":
        return call_doubao(api_key, prompt)
    elif model == "qwen":
        return call_qwen(api_key, prompt)
    else:
        raise Exception(f"不支持的模型: {model}")

def call_gemini(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 4096}
    }

    response = requests.post(url, json=data)
    result = response.json()

    # 检查是否有错误
    if "error" in result:
        error_msg = result["error"].get("message", "")
        if "API_KEY" in error_msg.upper():
            raise Exception("API Key无效，请检查侧边栏的API Key设置")
        raise Exception(f"API错误: {error_msg}")

    # 检查安全拦截
    prompt_feedback = result.get("promptFeedback", {})
    block_reason = prompt_feedback.get("blockReason", "")
    if block_reason:
        if block_reason == "PROHIBITED_CONTENT":
            raise Exception("⚠️ 内容包含敏感信息被拦截（暴力/血腥/违规内容），请修改故事素材后重试")
        elif block_reason == "SAFETY":
            raise Exception("⚠️ 内容触发安全过滤，请修改故事素材后重试")
        else:
            raise Exception(f"⚠️ 内容被拦截原因: {block_reason}，请修改故事素材后重试")

    # 检查返回内容是否为空
    candidates = result.get("candidates", [])
    if not candidates:
        raise Exception("API返回空结果，请重试")

    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        raise Exception("API返回内容为空，请重试")

    return result

def call_minimax(api_key, prompt):
    """MiniMax API调用"""
    url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "MiniMax-M2.7",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 4096,
        "thinking": {
            "type": "disabled"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"MiniMax API错误: HTTP {response.status_code} - {response.text}")

    result = response.json()

    if "error" in result:
        raise Exception(f"API错误: {result['error'].get('message', result['error'])}")

    return result

def call_doubao(api_key, prompt):
    """豆包API调用"""
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "doubao-seed-2-0-lite-260215",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 4096
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"豆包API错误: HTTP {response.status_code} - {response.text}")

    result = response.json()

    if "error" in result:
        raise Exception(f"API错误: {result['error'].get('message', result['error'])}")

    return result

def call_qwen(api_key, prompt):
    """通义千问API调用"""
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 4096
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "error" in result:
        raise Exception(f"API错误: {result['error'].get('message', result['error'])}")

    return result

def parse_response(response_text):
    # 提取JSON数组
    json_match = re.search(r'\[[\s\S]*\]', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            # 尝试修复不完整的JSON（截断情况）
            fixed_text = json_match.group()
            # 找到最后一个完整的对象
            last_complete_idx = fixed_text.rfind('},')
            if last_complete_idx != -1:
                try:
                    return json.loads(fixed_text[:last_complete_idx + 1] + ']')
                except:
                    pass
            # 尝试补全缺失的引号和括号
            if not fixed_text.strip().endswith(']'):
                fixed_text = fixed_text.rstrip(',') + '"]}'
            try:
                return json.loads(fixed_text)
            except:
                pass
    return None

def extract_content_from_response(model, result):
    """从不同模型的响应中提取文本内容"""
    if model == "gemini-2.5-pro":
        # Gemini 格式
        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    elif model in ["MiniMax-2.7", "doubao", "qwen"]:
        # OpenAI-compatible 格式
        choices = result.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""
    else:
        raise Exception(f"不支持的模型: {model}")

def transcribe_with_assemblyai(audio_data, filename, api_key):
    """使用AssemblyAI转写音视频"""
    # 上传文件
    upload_response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers={"authorization": api_key},
        data=audio_data
    )

    if upload_response.status_code != 200:
        raise Exception(f"上传失败: {upload_response.text}")

    audio_url = upload_response.json()["upload_url"]

    # 创建转写任务
    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers={"authorization": api_key},
        json={
            "audio_url": audio_url,
            "language_code": "zh"
        }
    )

    if transcript_response.status_code != 200:
        raise Exception(f"创建转写任务失败: {transcript_response.text}")

    transcript_id = transcript_response.json()["id"]

    # 轮询等待结果
    while True:
        status_response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers={"authorization": api_key}
        )

        status = status_response.json()["status"]

        if status == "completed":
            return status_response.json()["text"]
        elif status == "error":
            raise Exception("转写失败")
        else:
            time.sleep(3)

# 标题
st.title("🎬 错位创意生成器")
st.markdown("短剧素材创意生成工具 - 为广告优化师打造")

# 侧边栏 - API设置
with st.sidebar:
    st.header("⚙️ API 设置")

    # 模型选择
    selected_model = st.selectbox(
        "选择模型",
        options=list(MODEL_PRESETS.keys()),
        format_func=lambda x: MODEL_PRESETS[x]["name"],
        help="选择要使用的AI模型"
    )

    # 获取当前模型的配置
    model_config = MODEL_PRESETS[selected_model]

    # 动态API Key输入
    api_key = st.text_input(
        model_config["api_key_label"],
        type="password",
        help=model_config["api_key_help"]
    )

    st.markdown(f"[获取 {model_config['name']} API Key]({model_config['api_key_url']})")

    st.divider()

    # AssemblyAI
    assemblyai_key = st.text_input("AssemblyAI API Key（视频转写用）", type="password", help="在 assemblyai.com 获取，免费45分钟")

    if not assemblyai_key:
        st.info("如需视频转写功能，请输入 AssemblyAI API Key")
        st.markdown("[获取 AssemblyAI Key](https://www.assemblyai.com/)")

# 模式选择标签
tab1, tab2 = st.tabs(["🎯 错位创意生成", "🔄 反转剧情文案"])

# 模式1: 错位创意生成
with tab1:
    col1_disl, col2_disl = st.columns([1, 1.5])

    with col1_disl:
        st.subheader("📝 输入信息")

        # 目标用户 - 用下拉框选择预设，或选择"自定义"后输入
        target_user_option = st.selectbox("目标用户 *",
                                         ["自定义"] + TARGET_USER_PRESETS,
                                         index=0,
                                         help="从预设中选择或选择自定义")

        if target_user_option == "自定义":
            target_user = st.text_input("请输入目标用户", placeholder="例如：18-25岁女性 / 宝爸宝妈 / 打工人")
        else:
            target_user = target_user_option

        # 错位类型
        dislocation_type = st.selectbox("错位维度 *", [""] + DISLOCATION_TYPES)

        # 年代选择
        era_option = st.selectbox("年代（用于钩子）", [""] + ERA_PRESETS, help="选择钩子要设定的年代")

        # 目标素材（可选）
        material = st.text_area("目标素材（推广视频的旁白/文案）",
                              placeholder="不填写=自由发挥；填写=根据内容生成钩子+过渡+素材")

        # 参考创意（可选）
        reference = st.text_input("参考创意（可选）", placeholder="例如：类似XXX那种反差感")

        # 生成数量
        count = st.number_input("生成数量", min_value=1, max_value=20, value=5)

        # 生成按钮
        generate_btn = st.button("🚀 生成创意", type="primary", disabled=not api_key, key="generate_btn_1")

# 模式2: 反转剧情文案
with tab2:
    col1_twist, col2_twist = st.columns([1, 1.5])

    with col1_twist:
        st.subheader("📝 输入方向")

        # 方案选择
        approach_option = st.radio(
            "选择分析方案",
            ["方案1：方向提取（推荐）", "方案2：故事总结"],
            index=0,
            key="approach_radio",
            help="方案1侧重提取创作方向要素，方案2侧重完整故事分析"
        )

        # 保存方案选择到session_state
        st.session_state["use_direction_approach"] = "方案1" in approach_option

        # 视频上传
        st.markdown("**📹 上传视频（可选）**")
        video_file = st.file_uploader("支持 MP4/AVI/MOV/MKV 格式", type=["mp4", "avi", "mov", "mkv"], key="video_upload")

        if video_file and not assemblyai_key:
            st.error("请先在侧边栏输入 AssemblyAI API Key")

        if video_file and assemblyai_key:
            with st.spinner("视频转写中..."):
                try:
                    transcribed_text = transcribe_with_assemblyai(video_file.getvalue(), video_file.name, assemblyai_key)
                    st.success("✅ 转写完成")
                    st.session_state["transcribed_text"] = transcribed_text
                except Exception as e:
                    st.error(f"转写失败: {str(e)}")

        # 原始字幕/方向输入
        original_text = st.text_area(
            "📝 原文字幕 / 方向描述",
            placeholder="方式1：粘贴视频字幕，AI分析提取方向\n方式2：直接输入方向描述（如：婆媳冲突+彩礼+打脸）",
            value=st.session_state.get("transcribed_text", ""),
            height=150,
            key="original_text"
        )

        # 分析方向按钮
        analyze_btn = st.button("🔍 分析方向", type="secondary", disabled=not (api_key and original_text), key="analyze_btn")

        # 方向结果展示
        if "story_direction" in st.session_state and st.session_state["story_direction"]:
            st.markdown("---")
            st.subheader("📋 方案1结果：提取的方向")
            direction = st.session_state["story_direction"]
            direction_display = f"""**核心冲突:** {direction.get('核心冲突', '')}
**意象词:** {direction.get('意象词', '')}
**情绪基调:** {direction.get('情绪基调', '')}
**可用要素:** {direction.get('可用要素', '')}"""
            st.markdown(direction_display)

        # 总结结果展示
        if "story_summary" in st.session_state and st.session_state["story_summary"]:
            st.markdown("---")
            st.subheader("📋 方案2结果：故事总结")
            summary = st.session_state["story_summary"]
            summary_display = f"""**视角人物:** {summary.get('视角人物', '')}
**关系网:** {summary.get('关系网', '')}
**核心意象:** {', '.join(summary.get('核心意象', []))}
**核心冲突:** {summary.get('核心冲突', '')}
**情绪关键词:** {', '.join(summary.get('情绪关键词', []))}
**反转线索:** {summary.get('反转线索', '')}"""
            st.markdown(summary_display)

        st.markdown("---")

        # 生成参数
        st.subheader("🎯 生成设置")
        twist_count = st.number_input("生成数量", min_value=1, max_value=20, value=10, key="twist_count")
        duration = st.selectbox("时长", ["10秒", "15秒", "30秒", "60秒"], index=0)
        requirements = st.text_input("附加要求（可选）",
                                    placeholder="例如：第一人称、保留主人公等")

        # 生成按钮
        generate_twist_btn = st.button("🚀 生成文案", type="primary", disabled=not (api_key and ("story_direction" in st.session_state or "story_summary" in st.session_state)), key="generate_btn_2")

# 生成逻辑 - 模式1
if generate_btn:
    if not api_key:
        st.error("请先输入 API Key")
    elif not target_user:
        st.error("请输入目标用户")
    elif not dislocation_type:
        st.error("请选择错位维度")
    else:
        with st.spinner("创意生成中..."):
            try:
                input_data = {
                    "targetUser": target_user,
                    "dislocationType": dislocation_type,
                    "era": era_option if era_option else "不设限",
                    "material": material,
                    "reference": reference,
                    "count": count
                }

                prompt = get_prompt(input_data)
                result = call_api(selected_model, api_key, prompt)
                st.session_state["last_prompt"] = prompt
                st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)

                # 解析响应
                content = extract_content_from_response(selected_model, result)
                creatives = parse_response(content)

                if creatives:
                    st.session_state["creatives"] = creatives
                    st.session_state["has_material"] = bool(material)
                    st.session_state["current_mode"] = "dislocation"
                else:
                    st.error("无法解析结果，请查看下方调试信息")
                    with st.expander("🔧 调试信息（解析失败）"):
                        st.text_area("API返回内容", content if 'content' in dir() else str(result), height=300)

            except Exception as e:
                st.error(f"调用失败: {str(e)}")

# 分析逻辑
if analyze_btn:
    if not api_key:
        st.error("请先输入 API Key")
    elif not original_text:
        st.error("请输入原文字幕或方向描述")
    else:
        use_direction = st.session_state.get("use_direction_approach", True)
        spinner_text = "方向提取中..." if use_direction else "故事总结中..."

        with st.spinner(spinner_text):
            try:
                # 根据方案选择不同的prompt
                if use_direction:
                    prompt = get_direction_prompt(original_text)
                    result = call_api(selected_model, api_key, prompt)
                    st.session_state["last_prompt"] = prompt
                    st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)

                    # 解析响应
                    content = extract_content_from_response(selected_model, result)
                    direction = parse_response(content)

                    if direction and isinstance(direction, list) and len(direction) > 0 and isinstance(direction[0], dict):
                        st.session_state["story_direction"] = direction[0]
                        st.session_state["current_mode"] = "twist"
                        st.success("✅ 方向提取完成！可生成文案")
                        st.rerun()
                    else:
                        st.error("无法解析方向结果，请查看调试信息")
                        with st.expander("🔧 调试信息（解析失败）"):
                            st.text_area("API返回内容", content if content else str(result), height=300)
                else:
                    prompt = get_summary_prompt(original_text)
                    result = call_api(selected_model, api_key, prompt)
                    st.session_state["last_prompt"] = prompt
                    st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)

                    # 解析响应
                    content = extract_content_from_response(selected_model, result)
                    summary = parse_response(content)

                    if summary and isinstance(summary, list) and len(summary) > 0 and isinstance(summary[0], dict):
                        st.session_state["story_summary"] = summary[0]
                        st.session_state["current_mode"] = "twist"
                        st.success("✅ 故事总结完成！可生成文案")
                        st.rerun()
                    else:
                        st.error("无法解析总结结果，请查看调试信息")
                        with st.expander("🔧 调试信息（解析失败）"):
                            st.text_area("API返回内容", content if content else str(result), height=300)

            except Exception as e:
                st.error(f"调用失败: {str(e)}")

# 生成逻辑 - 模式2
if generate_twist_btn:
    if not api_key:
        st.error("请先输入 API Key")
    elif "story_direction" not in st.session_state and "story_summary" not in st.session_state:
        st.error("请先进行第一步：分析方向或总结故事")
    else:
        with st.spinner("文案生成中..."):
            try:
                use_direction = st.session_state.get("use_direction_approach", True)

                # 根据方案选择构建不同的素材描述
                if use_direction:
                    direction = st.session_state.get("story_direction", {})
                    story_material = f"""核心冲突：{direction.get('核心冲突', '')}
意象词：{direction.get('意象词', '')}
情绪基调：{direction.get('情绪基调', '')}
可用要素：{direction.get('可用要素', '')}"""
                else:
                    summary = st.session_state.get("story_summary", {})
                    story_material = f"""视角人物：{summary.get('视角人物', '')}
关系网：{summary.get('关系网', '')}
核心意象：{', '.join(summary.get('核心意象', []))}
核心冲突：{summary.get('核心冲突', '')}
情绪关键词：{', '.join(summary.get('情绪关键词', []))}
反转线索：{summary.get('反转线索', '')}"""

                prompt = get_plot_twist_prompt(story_material, twist_count, duration, requirements)
                result = call_api(selected_model, api_key, prompt)
                st.session_state["last_prompt"] = prompt
                st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)

                # 解析响应
                content = extract_content_from_response(selected_model, result)
                twists = parse_response(content)

                if twists:
                    st.session_state["twists"] = twists
                    st.session_state["current_mode"] = "twist"
                else:
                    st.error("无法解析结果，请查看下方调试信息")
                    with st.expander("🔧 调试信息（解析失败）"):
                        st.text_area("API返回内容", content, height=300)

            except Exception as e:
                st.error(f"调用失败: {str(e)}")

# 显示结果
current_mode = st.session_state.get("current_mode", "dislocation")

if current_mode == "dislocation" and "creatives" in st.session_state:
    has_material = st.session_state.get("has_material", False)

    with col2_disl:
        st.subheader(f"📋 生成的创意 ({len(st.session_state['creatives'])}条)" + (" - 自由发挥" if not has_material else ""))

        for i, creative in enumerate(st.session_state["creatives"]):
            with st.expander(f"创意 {i+1}", expanded=True):
                # 钩子
                st.markdown("### 🎣 钩子（基于错位）")
                st.markdown(f"**画面：** {creative.get('hookScene', '')}")
                st.markdown(f"**旁白：** {creative.get('hookNarration', '')}")

                # 如果有素材，显示过渡和素材
                if has_material:
                    # 过渡
                    st.markdown("### ➡️ 过渡（钩子→素材）")
                    st.info(creative.get('transition', ''))

                    # 素材
                    st.markdown("### 📦 素材（用户输入的内容）")
                    st.markdown(f"**旁白：** {creative.get('materialNarration', '')}")

                # 复制按钮
                if has_material:
                    copy_text = f"""【钩子 - 基于错位】
画面：{creative.get('hookScene', '')}
旁白：{creative.get('hookNarration', '')}

【过渡 - 衔接钩子和素材】
{creative.get('transition', '')}

【素材 - 用户输入的推广内容】
旁白：{creative.get('materialNarration', '')}"""
                else:
                    copy_text = f"""【钩子 - 基于错位】
画面：{creative.get('hookScene', '')}
旁白：{creative.get('hookNarration', '')}"""

                st.code(copy_text, language=None)

        # 调试模式
        with st.expander("🔧 调试信息"):
            st.text_area("发送的 Prompt", st.session_state.get("last_prompt", ""), height=200)
            st.text_area("API 原始响应", st.session_state.get("last_response", ""), height=300)

elif current_mode == "twist" and "twists" in st.session_state:
    with col2_twist:
        st.subheader(f"📋 生成的文案 ({len(st.session_state['twists'])}条)")

        # 一键复制全部
        all_copy = "\n\n".join([
            f"【{i+1}】{t.get('copy', '')}"
            for i, t in enumerate(st.session_state["twists"])
        ])
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            st.download_button("📋 复制全部文案", all_copy, file_name="文案.txt", use_container_width=True)

        # 紧凑网格展示
        cols = st.columns(2)
        for i, twist in enumerate(st.session_state["twists"]):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                        <span style="background: #e8f4ff; padding: 2px 8px; border-radius: 4px; margin-right: 5px;">{twist.get('conflict_angle', '')}</span>
                        <span style="background: #fff3e0; padding: 2px 8px; border-radius: 4px;">{twist.get('relationship', '')}</span>
                    </div>
                    <div style="font-size: 15px; font-weight: bold; margin: 8px 0;">{twist.get('copy', '')}</div>
                </div>
                """, unsafe_allow_html=True)

                # 单条复制按钮
                copy_text = twist.get('copy', '')
                st.download_button(f"📋 复制", copy_text, file_name=f"文案_{i+1}.txt", key=f"copy_btn_{i}", use_container_width=True)

        # 调试模式
        with st.expander("🔧 调试信息"):
            st.text_area("发送的 Prompt", st.session_state.get("last_prompt", ""), height=200)
            st.text_area("API 原始响应", st.session_state.get("last_response", ""), height=300)
