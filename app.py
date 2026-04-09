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

def get_plot_twist_prompt(story_material, count, duration, requirements):
    return f"""根据素材生成短剧文案。

## 素材
{story_material}

## 要求
- 生成{count}条
- 每条时长：{duration}
- 附加要求：{requirements}

## 创作方法
1. 从主人公特质出发，创造故事锚点（如：身体符号/物品符号/空间符号）
2. 识别核心冲突角度（如：至亲背叛/有能力者冷漠/后知后觉/被迫共犯/系统碾压）
3. 每条从不同关系切面出发，语气统一

## 输出格式（严格JSON）
[
  {{
    "copy": "文案内容（20-35字，2-3个逗号，结尾5字爆点）",
    "conflict_angle": "冲突角度",
    "relationship": "关系切面"
  }}
]

重要：只输出JSON数组！"""

def call_gemini_api(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 4096}
    }

    response = requests.post(url, json=data)
    return response.json()

def parse_response(response_text):
    # 提取JSON数组
    json_match = re.search(r'\[[\s\S]*\]', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    return None

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
    api_key = st.text_input("Google Gemini API Key", type="password", help="在 Google AI Studio 获取")
    assemblyai_key = st.text_input("AssemblyAI API Key（视频转写用）", type="password", help="在 assemblyai.com 获取，免费45分钟")

    if not api_key:
        st.warning("请输入 Google Gemini API Key")
        st.markdown("[获取 Gemini API Key](https://aistudio.google.com/app/apikey)")

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
        st.subheader("📝 故事素材")

        # 视频上传
        st.markdown("**📹 上传视频（可选）**")
        video_file = st.file_uploader("支持 MP4/AVI/MOV/MKV 格式", type=["mp4", "avi", "mov", "mkv"], key="video_upload")

        if video_file and not assemblyai_key:
            st.error("请先在侧边栏输入 AssemblyAI API Key")

        if video_file and assemblyai_key:
            with st.spinner("视频上传中..."):
                try:
                    transcribed_text = transcribe_with_assemblyai(video_file.getvalue(), video_file.name, assemblyai_key)
                    st.success("✅ 转写完成")
                    st.session_state["transcribed_text"] = transcribed_text
                except Exception as e:
                    st.error(f"处理失败: {str(e)}")

        # 显示转写结果
        if "transcribed_text" in st.session_state and st.session_state["transcribed_text"]:
            st.text_area("📝 转写结果（可编辑）", st.session_state["transcribed_text"], height=100, key="transcribed_display")

        # 故事素材
        story_material = st.text_area("故事素材（人物+关系+极端事件） *",
                                     placeholder="例如：弟弟是公司CEO，哥哥是建筑工人，两人是亲兄弟",
                                     value=st.session_state.get("transcribed_text", ""),
                                     height=120)

        # 生成数量
        twist_count = st.number_input("生成数量", min_value=1, max_value=20, value=10, key="twist_count")

        # 时长选择
        duration = st.selectbox("时长", ["10秒", "15秒", "30秒", "60秒"], index=0)

        # 附加要求
        requirements = st.text_input("附加要求（可选）",
                                    placeholder="例如：第一人称、保留主人公等")

        # 生成按钮
        generate_twist_btn = st.button("🚀 生成文案", type="primary", disabled=not api_key, key="generate_btn_2")

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
                result = call_gemini_api(api_key, prompt)

                # 解析响应
                content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                creatives = parse_response(content)

                if creatives:
                    st.session_state["creatives"] = creatives
                    st.session_state["has_material"] = bool(material)
                    st.session_state["last_prompt"] = prompt
                    st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)
                    st.session_state["current_mode"] = "dislocation"
                else:
                    st.error("无法解析结果，请重试")

            except Exception as e:
                st.error(f"调用失败: {str(e)}")

# 生成逻辑 - 模式2
if generate_twist_btn:
    if not api_key:
        st.error("请先输入 API Key")
    elif not story_material:
        st.error("请输入故事素材")
    else:
        with st.spinner("文案生成中..."):
            try:
                prompt = get_plot_twist_prompt(story_material, twist_count, duration, requirements)
                result = call_gemini_api(api_key, prompt)

                # 解析响应
                content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                twists = parse_response(content)

                if twists:
                    st.session_state["twists"] = twists
                    st.session_state["last_prompt"] = prompt
                    st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)
                    st.session_state["current_mode"] = "twist"
                else:
                    st.error("无法解析结果，请重试")

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

        for i, twist in enumerate(st.session_state["twists"]):
            with st.expander(f"文案 {i+1}", expanded=True):
                # 显示标签
                col_tag1, col_tag2 = st.columns(2)
                with col_tag1:
                    st.markdown(f"**🏷️ 冲突角度：** {twist.get('conflict_angle', '')}")
                with col_tag2:
                    st.markdown(f"**🔗 关系切面：** {twist.get('relationship', '')}")

                # 文案内容 - 突出显示
                st.markdown(f"### 📝 {twist.get('copy', '')}")

                # 复制按钮
                copy_text = f"""【冲突角度】
{twist.get('conflict_angle', '')}

【关系切面】
{twist.get('relationship', '')}

【文案】
{twist.get('copy', '')}"""

                st.code(copy_text, language=None)

        # 调试模式
        with st.expander("🔧 调试信息"):
            st.text_area("发送的 Prompt", st.session_state.get("last_prompt", ""), height=200)
            st.text_area("API 原始响应", st.session_state.get("last_response", ""), height=300)
