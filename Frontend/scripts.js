const chatContainer = document.querySelector(".chat-container");
const chatBox = document.querySelector(".chat-box");
const input = document.querySelector(".user-input");
const sendBtn = document.querySelector(".send-button");
const messagesDiv = document.querySelector(".messages");

let sessionId = null;

// Get session from backend
async function initSession() {
  try {
    const res = await fetch("http://127.0.0.1:8000/session", {
      method: "POST",
    });
    const data = await res.json();
    sessionId = data.session_id;
  } catch (err) {
    console.error("Session init failed:", err);
  }
}
initSession();

function appendMessage(text, cls) {
  const div = document.createElement("div");
  div.classList.add("message", cls);
  div.innerText = text;
  messagesDiv.appendChild(div);

  setTimeout(() => {
    messagesDiv.scrollTo({
      top: messagesDiv.scrollHeight,
      behavior: "smooth",
    });
  }, 50);

  return div;
}

// Show typing indicator
function showTyping() {
  const div = document.createElement("div");
  div.classList.add("message", "bot-msg");
  div.innerText = "Empathia is typing...";
  div.dataset.typing = "1";
  messagesDiv.appendChild(div);

  setTimeout(() => {
    messagesDiv.scrollTo({
      top: messagesDiv.scrollHeight,
      behavior: "smooth",
    });
  }, 50);

  return div;
}

// Send message to backend
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // User message
  appendMessage(text, "user-msg");

  // Clear input
  input.value = "";

  // Show typing
  const typingEl = showTyping();

  try {
    const res = await fetch("http://127.0.0.1:8000/respond", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: text, session_id: sessionId }),
    });

    const data = await res.json();

    // Remove typing
    if (typingEl && typingEl.parentNode) typingEl.remove();

    // Bot reply
    appendMessage(data.response, "bot-msg");

    // Update session
    sessionId = data.session_id;
  } catch (err) {
    console.error("Error:", err);
    if (typingEl && typingEl.parentNode) typingEl.remove();
    appendMessage(
      "Sorry, I'm having trouble connecting. Please try again.",
      "bot-msg"
    );
  }
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Modal handling
const modal = document.getElementById("gameModal");
const btn = document.querySelector(".game-menu-btn");
const span = document.querySelector(".close");
const gameFrame = document.getElementById("gameFrame");

btn.onclick = () => {
  modal.style.display = "block";
};

span.onclick = () => {
  modal.style.display = "none";
  gameFrame.src = "";
};

window.onclick = (event) => {
  if (event.target == modal) {
    modal.style.display = "none";
    gameFrame.src = "";
  }
};

function loadGame(gameFile) {
  gameFrame.src = gameFile;
}

// Auto-focus input when page loads
window.addEventListener("load", () => {
  input.focus();
});
