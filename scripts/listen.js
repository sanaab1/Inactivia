const lines = [];
let listening = false;

const cleanedChunks = [];
let cleanedUpTo = 0;
let cleaning = false;
const BATCH_SIZE = 4;

const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
rec.continuous = true;
rec.interimResults = true;
rec.lang = 'en-US';

rec.onresult = (e) => {
  let interim = '';

  for (let i = e.resultIndex; i < e.results.length; i++) {
    const text = e.results[i][0].transcript;
    if (e.results[i].isFinal) {
      lines.push({ text: text.trim(), time: Date.now() });
      if (lines.length - cleanedUpTo >= BATCH_SIZE) cleanNewLines();
    } else {
      interim += text;
    }
  }

  render(interim);
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
  cleanNewLines();
};

function tidy(text) {
  const t = text.trim();
  if (!t) return '';
  const capped = t.charAt(0).toUpperCase() + t.slice(1);
  return /[.?!]$/.test(capped) ? capped : capped + '.';
}

function render(interim = '') {
  const box = document.getElementById('live');
  box.innerHTML = '';

  cleanedChunks.forEach(chunk => {
    const d = document.createElement('div');
    d.textContent = chunk;
    d.style.whiteSpace = 'pre-wrap';
    d.style.marginBottom = '0.8em';
    box.appendChild(d);
  });

  const pendingText = lines.slice(cleanedUpTo).map(l => tidy(l.text)).join(' ');
  const grey = (pendingText + ' ' + interim).trim();
  if (grey) {
    const d = document.createElement('div');
    d.textContent = grey;
    d.style.color = '#888';
    box.appendChild(d);
  }
}

async function cleanNewLines() {
  if (cleaning) return;
  const pending = lines.slice(cleanedUpTo);
  if (pending.length === 0) return;

  cleaning = true;
  const end = cleanedUpTo + pending.length;

  try {
    const res = await fetch('/api/clean', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ text: pending.map(l => l.text).join(' ') }),
    });
    const data = await res.json();
    if (data.clean) {
      cleanedChunks.push(data.clean);
      cleanedUpTo = end;
    } else {
      console.log('Clean failed:', data.error || data);
    }
  } catch (err) {
    console.log('Clean error:', err);
  }

  cleaning = false;
  render();
}

setInterval(cleanNewLines, 15000);

async function triggerScan() {
    const transcriptText = document.getElementById('live').innerText;
    const sidebarDiv = document.getElementById('sidebar-questions');

    if (!transcriptText || transcriptText.trim() === "") {
        alert("No transcript text found to scan yet!");
        return;
    }

    try {
        const response = await fetch('/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: transcriptText })
        });

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            if (sidebarDiv.querySelector('.placeholder-text')) {
                sidebarDiv.innerHTML = '';
            }

            data.results.forEach(item => {
              const safeId = "q-" + btoa(item.question).replace(/=/g, '').substring(0, 15);
              if (!document.getElementById(safeId)) {
                  const card = document.createElement('div');
                  card.id = safeId;
                  card.className = 'question-card';
                  
                  card.innerHTML = `
                      <div class="card-header">
                          <p class="question-title"><strong>${item.question}</strong></p>
                          <button class="delete-btn" title="Remove question">&times;</button>
                      </div>
                      <div class="answer-box" style="display: none;">
                          <p><strong>Answer:</strong></p>
                          <div>${item.answer.replace(/\n/g, '<br>')}</div>
                      </div>
                  `;

                  card.onclick = () => {
                      const answerBox = card.querySelector('.answer-box');
                      if (answerBox.style.display === 'none') {
                          answerBox.style.display = 'block';
                          card.classList.add('active');
                      } else {
                          answerBox.style.display = 'none';
                          card.classList.remove('active');
                      }
                  };

                  const deleteBtn = card.querySelector('.delete-btn');
                  deleteBtn.onclick = (e) => {
                      e.stopPropagation();
                      card.remove();
                  };

                  sidebarDiv.prepend(card);
              }
          });
        }
    } catch (err) {
        console.error("Error communicating with AI backend:", err);
    }
}