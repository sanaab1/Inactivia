export default async function handler(req, res) {
  const { text } = req.body;

  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-5-5',
      max_tokens: 1500,
      system: 'You clean up raw speech-to-text from a classroom lesson. Add punctuation and capitalization, split into short paragraphs, and fix obvious misheard words using context. Do not add, remove, or summarize content. Return only the cleaned text.',
      messages: [{ role: 'user', content: text }],
    }),
  });

  const data = await r.json();
  res.status(200).json({ clean: data.content[0].text });
}

let cleanText = '';

async function cleanTranscript() {
  const raw = lines.map(l => l.text).join(' ');
  const res = await fetch('/api/clean', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ text: raw }),
  });
  const data = await res.json();
  cleanText = data.clean;
  document.getElementById('live').innerText = cleanText;
}