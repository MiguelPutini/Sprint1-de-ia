// ─── SHARED ──────────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem('ev_token'); }
function authHeaders() { return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` }; }
function logout() { localStorage.removeItem('ev_token'); window.location.href = '/'; }

if (!getToken()) { window.location.href = '/'; }

// ─── CHAT STATE ───────────────────────────────────────────────────────────────
let isTyping = false;

// ─── INIT ─────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  addMessage('ai', '👋 Olá! Sou o assistente do **EV Charge SP**.\n\nConsulto apenas os dados reais da sua conta no banco de dados.\n\nDigite **ajuda** para ver o que posso responder ou use as sugestões abaixo!');
  document.getElementById('chatInput').focus();
});

// ─── SEND ─────────────────────────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg || isTyping) return;
  input.value = '';

  addMessage('user', msg);
  setTyping(true);

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ message: msg })
    });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    addMessage('ai', data.response || 'Sem resposta.');
  } catch (e) {
    addMessage('ai', '❌ Erro de conexão. Verifique se o servidor está rodando.');
  } finally {
    setTyping(false);
  }
}

function sendSuggestion(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

// ─── RENDER ───────────────────────────────────────────────────────────────────
function addMessage(role, text) {
  const box = document.getElementById('chatMessages');
  const isAI = role === 'ai';

  const wrapper = document.createElement('div');
  wrapper.className = `chat-msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'chat-avatar';
  avatar.textContent = isAI ? '🤖' : '👤';

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.innerHTML = formatText(text);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  box.appendChild(wrapper);
  box.scrollTop = box.scrollHeight;
}

function formatText(text) {
  // Bold **text**
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
}

function setTyping(active) {
  isTyping = active;
  const btn = document.getElementById('btnSend');
  const input = document.getElementById('chatInput');
  btn.disabled = active;
  input.disabled = active;

  const existing = document.getElementById('typingIndicator');
  if (active && !existing) {
    const box = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.className = 'chat-msg ai';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble chat-typing">
        <span style="display:inline-flex;gap:4px;align-items:center;">
          <span style="animation:bounce 0.8s infinite 0s">●</span>
          <span style="animation:bounce 0.8s infinite 0.15s">●</span>
          <span style="animation:bounce 0.8s infinite 0.3s">●</span>
        </span>
        <style>@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}</style>
      </div>`;
    box.appendChild(indicator);
    box.scrollTop = box.scrollHeight;
  } else if (!active && existing) {
    existing.remove();
  }
}

function clearChat() {
  document.getElementById('chatMessages').innerHTML = '';
  addMessage('ai', '🗑️ Conversa limpa! Como posso ajudar?');
}
