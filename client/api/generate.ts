export const dynamic = 'force-dynamic'

export async function POST(request: Request) {
  const body = await request.json()

  const apiKey = body.apiKey
  const prompt = body.prompt

  if (!apiKey || !prompt) {
    return Response.json({ error: 'Missing apiKey or prompt' }, { status: 400 })
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.9, maxOutputTokens: 4096 }
        })
      }
    )

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}
