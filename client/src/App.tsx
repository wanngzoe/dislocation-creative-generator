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
    const { targetUser, dislocationType, description, reference, count } = input
    return `为短剧广告生成恰好${count}条错位素材创意。

目标受众：${targetUser}
错位类型：${dislocationType}
核心内容：${description}
${reference ? `参考风格：${reference}` : ''}

要求：
1. 专为短剧引流广告设计，激发用户点击观看欲望
2. 利用${dislocationType}制造强烈反差和悬念
3. 画面描述：50-80字，适合5-15秒短视频，要有画面感、有人物状态和情绪
4. 旁白文案：10-20字，口语化、有情绪、能引发好奇
5. 开头要有吸引力，能抓住眼球

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
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apiKey,
          prompt: getPrompt(input)
        }),
      })

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
      setError(err instanceof Error ? err.message : '生成失败，请重试')
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
