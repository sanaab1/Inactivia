const lines = [];
let listening = false;

const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
rec.continuous = true;
rec.interimResults = true;
rec.lang = 'en-US';

rec.onresult = (e) => {
  for (let i = e.resultIndex; i < e.results.length; i++) {
    if (e.results[i].isFinal) {
      lines.push({ text: e.results[i][0].transcript.trim(), time: Date.now() });
    }
  }
  document.getElementById('live').textContent = lines.map(l => l.text).join(' ');
};

rec.onend = () => {
  if (listening) setTimeout(() => rec.start(), 300);
};

rec.onerror = (e) => console.log('Speech error:', e.error);

document.getElementById('listenButton').onclick = () => {
  if (!listening) {
    listening = true;
    rec.start();
  }
};

document.getElementById('stopButton').onclick = () => {
  listening = false;
  rec.stop();
};

document.getElementById('saveButton').onclick = () => {
  const text = lines
    .map(l => `[${new Date(l.time).toLocaleTimeString()}] ${l.text}`)
    .join('\n');
  const blob = new Blob([text], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'transcript.txt';
  a.click();
  URL.revokeObjectURL(a.href);
};

function tidy(text) {
  const t = text.trim();
  if (!t) return '';
  const capped = t.charAt(0).toUpperCase() + t.slice(1);
  return /[.?!]$/.test(capped) ? capped : capped + '.';
}

function render() {
  const box = document.getElementById('live');
  box.innerHTML = '';
  lines.forEach(l => {
    const d = document.createElement('div');
    d.textContent = tidy(l.text);
    box.appendChild(d);
  });
}

rec.onresult = (e) => {
  let interim = '';

  for (let i = e.resultIndex; i < e.results.length; i++) {
    const text = e.results[i][0].transcript;
    if (e.results[i].isFinal) {
      const line = { text: text.trim(), time: Date.now() };
      lines.push(line);
      appendToFile(`[${new Date(line.time).toLocaleTimeString()}] ${line.text}`);
    } else {
      interim += text;
    }
  }

  render(interim);
};

function render(interim = '') {
  const box = document.getElementById('live');
  box.innerHTML = '';
  lines.forEach(l => {
    const d = document.createElement('div');
    d.textContent = tidy(l.text);
    box.appendChild(d);
  });
  if (interim) {
    const d = document.createElement('div');
    d.textContent = interim;
    d.style.color = '#888';
    box.appendChild(d);
  }
}