import streamlit as st
import requests
import json
import re

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

def get_prompt(input_data):
    target_user = input_data["targetUser"]
    dislocation_type = input_data["dislocationType"]
    era = input_data.get("era", "不设限")
    material = input_data["material"]
    reference = input_data.get("reference", "")
    count = input_data["count"]

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

# 标题
st.title("🎬 错位创意生成器")
st.markdown("短剧素材创意生成工具 - 为广告优化师打造")

# 侧边栏 - API设置
with st.sidebar:
    st.header("⚙️ API 设置")
    api_key = st.text_input("Google Gemini API Key", type="password", help="在 Google AI Studio 获取")

    if not api_key:
        st.warning("请输入 API Key")
        st.markdown("[获取 API Key](https://aistudio.google.com/app/apikey)")

# 主界面 - 输入表单
col1, col2 = st.columns([1, 1.5])

with col1:
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

    # 目标素材 - 改为推广视频的旁白/文案
    material = st.text_area("目标素材（推广视频的旁白/文案） *",
                          placeholder="例如：霸道总裁发现女主是自己失散多年的妹妹，两人经历误会后最终相认")

    # 参考创意（可选）
    reference = st.text_input("参考创意（可选）", placeholder="例如：类似XXX那种反差感")

    # 生成数量
    count = st.number_input("生成数量", min_value=1, max_value=20, value=5)

    # 生成按钮
    generate_btn = st.button("🚀 生成创意", type="primary", disabled=not api_key)

# 生成逻辑
if generate_btn:
    if not api_key:
        st.error("请先输入 API Key")
    elif not target_user:
        st.error("请输入目标用户")
    elif not dislocation_type:
        st.error("请选择错位维度")
    elif not material:
        st.error("请输入目标素材")
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
                    st.session_state["last_prompt"] = prompt
                    st.session_state["last_response"] = json.dumps(result, indent=2, ensure_ascii=False)
                else:
                    st.error("无法解析结果，请重试")

            except Exception as e:
                st.error(f"调用失败: {str(e)}")

# 显示结果
if "creatives" in st.session_state:
    with col2:
        st.subheader(f"📋 生成的创意 ({len(st.session_state['creatives'])}条)")

        for i, creative in enumerate(st.session_state["creatives"]):
            with st.expander(f"创意 {i+1}", expanded=True):
                # 钩子
                st.markdown("### 🎣 钩子（基于错位）")
                st.markdown(f"**画面：** {creative.get('hookScene', '')}")
                st.markdown(f"**旁白：** {creative.get('hookNarration', '')}")

                # 过渡
                st.markdown("### ➡️ 过渡（钩子→素材）")
                st.info(creative.get('transition', ''))

                # 素材
                st.markdown("### 📦 素材（用户输入的内容）")
                st.markdown(f"**旁白：** {creative.get('materialNarration', '')}")

                # 复制按钮
                copy_text = f"""【钩子 - 基于错位】
画面：{creative.get('hookScene', '')}
旁白：{creative.get('hookNarration', '')}

【过渡 - 衔接钩子和素材】
{creative.get('transition', '')}

【素材 - 用户输入的推广内容】
旁白：{creative.get('materialNarration', '')}"""

                st.code(copy_text, language=None)

        # 调试模式
        with st.expander("🔧 调试信息"):
            st.text_area("发送的 Prompt", st.session_state.get("last_prompt", ""), height=200)
            st.text_area("API 原始响应", st.session_state.get("last_response", ""), height=300)
