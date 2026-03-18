import { useState } from 'react'
import { CreativeInput, Creative } from './types'
import { DISLOCATION_TYPES, TARGET_USER_PRESETS } from './constants'

function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('gemini_api_key') || '')
  const [input, setInput] = useState<CreativeInput>({
    targetUser: '',
    dislocationType: '',
    description: '',
    reference: '',
    industry: '短剧',
    count: 5,
  })
  const [creatives, setCreatives] = useState<Creative[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')
  const [showSettings, setShowSettings] = useState(!apiKey)
  const [debugMode, setDebugMode] = useState(false)
  const [debugInfo, setDebugInfo] = useState<{ prompt: string; response: string } | null>(null)

  const saveApiKey = (key: string) => {
    setApiKey(key)
    localStorage.setItem('gemini_api_key', key)
    setShowSettings(false)
  }

  const getPrompt = (input: CreativeInput) => {
    const { targetUser, dislocationType, description, reference } = input
    const count = input.count
    return `生成恰好${count}条短剧广告引流素材创意，结合传播学、心理学与爆款案例，生成高点击率、高转化率的创意内容。

## 基础信息
目标受众：${targetUser}
错位类型：${dislocationType}
核心内容：${description}
${reference ? `参考风格：${reference}` : ''}

## 错位维度体系（20种）
1. 职业错位 - 不同职业之间的反差（如程序员在手术室写代码）
2. 年龄错位 - 不同年龄段之间的反差（如小孩签合同、老人扣篮）
3. 性别错位 - 性别角色的反差（如男性美甲师、女性搬砖）
4. 时代错位 - 不同时代的反差（如古人用智能手机）
5. 物种错位 - 人与动物的反差（如猫当老板、熊猫打螺丝）
6. 场景错位 - 不同场景的反差（如潜水员在沙漠、消防员在雪山）
7. 材质/形态错位 - 材质或形态的反差（如人变成红绿灯、沙发成精）
8. 语言/文化错位 - 语言或文化的反差（如老外说相声）
9. 关系错位 - 不同关系的反差（如父亲给女儿当伴娘）
10. 声音/语言错位 - 声音或语言的反差（如糙汉子声音却是萌妹子）
11. 身份/阶层错位 - 身份或阶层的反差（如流浪汉穿高定、富豪吃烤串）
12. 比例/尺度错位 - 比例或尺度的反差（如巨人玩蚂蚁、头变成篮球大小）
13. 状态/情绪错位 - 状态或情绪的反差（如葬礼载歌载舞、中奖反而哭）
14. 季节/温度错位 - 季节或温度的反差（如夏天穿羽绒服堆雪人）
15. 风格/艺术错位 - 风格或艺术的反差（如兵马俑穿JK）
16. 虚拟与现实错位 - 虚拟与现实的反差（如NPC送外卖）
17. 职业与技能错位 - 职业与技能的反差（如rapper念政府工作报告）
18. 因果错位 - 因果关系的反差（如吃方便面住别墅）
19. 数字/数据错位 - 数字或数据的反差（如100岁过1岁生日）
20. 组合错位 - 多维度叠加的反差（如古代皇帝用手机治国）

## 传播学与心理学核心技巧

### 1. 注意力捕获
- 开头必须抓眼球：用异常画面、冲突台词、悬念
- 利用"认知缺口"：让用户想知道"后续发生了什么"
- 祖母法则：先说结果/好处

### 2. 情绪共鸣
- 激发情绪：好奇、惊讶、愤怒、焦虑、羡慕、爽感
- 利用"损失厌恶"：错过就没了、仅限今天
- 利用"社会认同"：大家都在看

### 3. 认知反差
- 错位越明显，冲击力越强
- 制造"这不可能但又发生了"的感觉
- 但要合理可执行，AI能呈现

### 4. 行动号召
- 旁白口语化、接地气
- 留悬念：想知道后续？去看完整短剧

## 创意参考风格（来自爆款案例）

优秀案例特点：
- 画面描述简洁有力，一句话就能脑补画面
- 旁白文案10-20字，是点睛之笔
- 有反转/槽点/金句，让人印象深刻
- 能激发情绪反应

示例：
- "穿白大褂的程序员在写代码，背景是手术室" → "这代码，是救命的还是致病的？"
- "老人在篮球场扣篮，身穿高中生校服" → "谁还没年轻过？但这也太能了"
- "小孩在办公桌前签合同，旁边堆满文件" → "这届小孩，活得比大人还累"

## 创意要求

1. 专为短剧引流广告设计，目标：让用户点击进入短剧
2. 利用${dislocationType}制造强烈认知反差
3. 画面描述：50-80字，适合5-15秒短视频
   - 简洁有力，一句话脑补画面
   - 有人物、场景、动作
   - 开头抓眼球，有冲突/悬念
4. 旁白文案：10-20字
   - 口语化、有情绪、能引发好奇
   - 有反转/槽点/金句感
   - 引导点击去看完整短剧
5. 每条创意都要有"钩子"，让人想看后续

返回JSON数组：
[{"scene":"画面描述","narration":"旁白文案"}]`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!apiKey) {
      setShowSettings(true)
      return
    }

    setLoading(true)
    setError('')
    setCreatives([])

    try {
      // 添加超时控制
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60秒超时

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apiKey,
          prompt: getPrompt(input)
        }),
        signal: controller.signal
      })
      clearTimeout(timeoutId)

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.error?.message || 'API 调用失败')
      }

      const data = await response.json()
      const content = data.candidates?.[0]?.content?.parts?.[0]?.text || ''

      if (debugMode) {
        setDebugInfo({
          prompt: getPrompt(input),
          response: JSON.stringify(data, null, 2)
        })
      }

      const jsonMatch = content.match(/\[[\s\S]*\]/)
      if (!jsonMatch) throw new Error('无法解析结果')

      const parsed = JSON.parse(jsonMatch[0])
      setCreatives(parsed.map((item: any, index: number) => ({
        id: `creative-${Date.now()}-${index}`,
        sceneDescription: item.scene || item.sceneDescription || '',
        narration: item.narration || '',
      })))
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '生成失败，请重试'
      // 如果是网络错误，给出更具体的提示
      if (errorMsg.includes('Failed to fetch') || errorMsg.includes('network')) {
        setError('网络连接失败，请检查网络后重试')
      } else {
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setToast('已复制到剪贴板')
    setTimeout(() => setToast(''), 2000)
  }

  const formatCreative = (creative: Creative) => {
    return `画面描述：${creative.sceneDescription}\n旁白文案：${creative.narration}`
  }

  return (
    <div className="container">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>错位创意生成器</h1>
            <p>短剧素材创意生成工具 - 为广告优化师打造</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className={`btn-icon ${debugMode ? 'active' : ''}`}
              onClick={() => { setDebugMode(!debugMode); setDebugInfo(null) }}
              title="调试模式"
              style={{ color: debugMode ? 'var(--primary)' : undefined }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
              </svg>
            </button>
            <button className="btn-icon" onClick={() => setShowSettings(true)} title="API 设置">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <div className="main-layout">
        <form className="form-card" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>
              目标用户 <span className="required">*</span>
            </label>
            <input
              type="text"
              value={input.targetUser}
              onChange={(e) => setInput({ ...input, targetUser: e.target.value })}
              placeholder="例如：18-25岁女性 / 宝爸宝妈 / 打工人"
              required
            />
            <div className="quick-tags">
              {TARGET_USER_PRESETS.map((preset) => (
                <span
                  key={preset}
                  className="quick-tag"
                  onClick={() => setInput({ ...input, targetUser: preset })}
                >
                  {preset}
                </span>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>
              错位维度 <span className="required">*</span>
            </label>
            <select
              value={input.dislocationType}
              onChange={(e) => setInput({ ...input, dislocationType: e.target.value })}
              required
            >
              <option value="">选择错位类型</option>
              {DISLOCATION_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>
              素材描述/故事梗概 <span className="required">*</span>
            </label>
            <textarea
              value={input.description}
              onChange={(e) => setInput({ ...input, description: e.target.value })}
              placeholder="例如：一个程序员转型做早餐店 / 老年人学年轻人穿搭"
              required
            />
          </div>

          <div className="form-group">
            <label>参考创意（可选）</label>
            <input
              type="text"
              value={input.reference}
              onChange={(e) => setInput({ ...input, reference: e.target.value })}
              placeholder="例如：类似XXX那种反差感"
            />
          </div>

          <div className="form-group">
            <label>
              生成数量 <span className="required">*</span>
            </label>
            <input
              type="number"
              min={1}
              max={20}
              value={input.count}
              onChange={(e) => setInput({ ...input, count: parseInt(e.target.value) || 5 })}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '生成中...' : '生成创意'}
          </button>
        </form>

        <section className="results-section">
          {error && <div className="error-message">{error}</div>}

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>创意生成中，请稍候...</p>
            </div>
          )}

          {!loading && creatives.length > 0 && (
            <>
              <div className="results-header">
                <h2>生成的创意 ({creatives.length}条)</h2>
              </div>
              <div className="creatives-grid">
                {creatives.map((creative, index) => (
                  <div key={creative.id} className="creative-card">
                    <div className="scene-label">
                      <span className="index">{index + 1}</span>
                      画面描述
                    </div>
                    <p className="scene-description">{creative.sceneDescription}</p>
                    <p className="narration-label">旁白文案</p>
                    <p className="narration">{creative.narration}</p>
                    <div className="actions">
                      <button
                        className="btn btn-secondary"
                        onClick={() => copyToClipboard(formatCreative(creative))}
                      >
                        复制
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {!loading && creatives.length === 0 && !error && (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
              </svg>
              <p>填写左侧表单，点击"生成创意"</p>
              <p>AI 将根据错位规则生成原创创意文案</p>
            </div>
          )}

          {debugMode && debugInfo && (
            <div className="debug-panel">
              <h3>调试信息</h3>
              <div className="debug-section">
                <h4>发送的 Prompt</h4>
                <pre>{debugInfo.prompt}</pre>
              </div>
              <div className="debug-section">
                <h4>API 原始响应</h4>
                <pre>{debugInfo.response}</pre>
              </div>
            </div>
          )}
        </section>
      </div>

      {toast && <div className="toast">{toast}</div>}

      {showSettings && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>API 设置</h3>
            <p className="modal-desc">请输入你的 Google Gemini API Key（仅本地存储，不上传）</p>
            <input
              type="password"
              placeholder="AIzaSy..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="api-key-input"
            />
            <p className="modal-hint">
              获取 API Key：<a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener">Google AI Studio</a>
            </p>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={() => saveApiKey(apiKey)}>
                保存并使用
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
