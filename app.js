//  http://localhost:5005/webhooks/rest/webhook
const RASA_BASE_URL = "http://localhost:5005";
const REST_WEBHOOK = `${RASA_BASE_URL}/webhooks/rest/webhook`;

// Mỗi lần refresh sẽ có sender mới trong session => mở chat là greet lại
const SENDER_ID = sessionStorage.getItem("tvu_sender") || (() => {
  const id = "web_" + Math.random().toString(16).slice(2);
  sessionStorage.setItem("tvu_sender", id);
  return id;
})();

const panel = document.getElementById("chatPanel");
const body = document.getElementById("chatBody");
const input = document.getElementById("chatInput");

function addMsg(text, who) {
  const wrap = document.createElement("div");
  wrap.className = "msg " + who;
  const b = document.createElement("div");
  b.className = "bubble-msg";
  b.textContent = text;
  wrap.appendChild(b);
  body.appendChild(wrap);
  body.scrollTop = body.scrollHeight;
}
function addUser(text) { addMsg(text, "user"); }
function addBot(text) { addMsg(text, "bot"); }

async function sendToRasa(message, showUserBubble = true) {
  if (showUserBubble) addUser(message);

  try {
    const res = await fetch(REST_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender: SENDER_ID, message })
    });

    if (!res.ok) {
      addBot('Mình chưa kết nối được server Rasa. Hãy chạy: rasa run --enable-api --cors "*" --port 5005');
      return;
    }

    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      addBot("Mình chưa có phản hồi từ bot cho câu này.");
      return;
    }

    for (const m of data) {
      if (m.text) addBot(m.text);
      else if (m.image) addBot("Ảnh: " + m.image);
      else addBot("Bot có phản hồi dạng khác (buttons/attachment) nhưng web chưa hỗ trợ hiển thị.");
    }
  } catch (e) {
    addBot("Có lỗi khi gọi REST API. Bạn kiểm tra CORS / URL server Rasa nhé.");
  }
}

function openChat() {
  panel.style.display = "block";
  setTimeout(() => input.focus(), 0);

  // Tự động chào 1 lần mỗi lần mở chat
  if (!window.__tvu_greeted) {
    window.__tvu_greeted = true;
    sendToRasa("/greet", false); // không hiện bubble user
  }
}

function closeChat() { panel.style.display = "none"; }

function toggleChat() {
  const isOpen = panel.style.display === "block";
  if (isOpen) closeChat();
  else openChat();
}

function quickAsk(text) {
  openChat();
  input.value = text;
  send();
}

async function send() {
  const text = (input.value || "").trim();
  if (!text) return;
  input.value = "";
  await sendToRasa(text, true);
}

// Enter to send
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});
