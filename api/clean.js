const MODEL = 'gpt-4o-mini';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const { text } = req.body;

  try {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        max_completion_tokens: 1500,
        messages: [
          {
            role: 'system',
            content:
              'You clean up raw speech-to-text from a classroom lesson. Add punctuation and capitalization, split into short paragraphs, and fix obvious misheard words using context. Do not add, remove, or summarize content. Return only the cleaned text.',
          },
          { role: 'user', content: text },
        ],
      }),
    });

    const data = await r.json();
    if (!r.ok) console.log('OpenAI error:', data.error);
    if (!r.ok) return res.status(500).json({ error: data.error?.message || 'API error' });

    res.status(200).json({ clean: data.choices[0].message.content });
  } catch (err) {
    res.status(500).json({ error: 'Something went wrong' });
  }
}