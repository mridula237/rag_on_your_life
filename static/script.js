const chat = document.getElementById("chat");
const input = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const sourcesDiv = document.getElementById("sources");

let hasUploaded = false;

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function renderSources(sources) {
  if (!sources || sources.length === 0) {
    sourcesDiv.innerHTML = "";
    return;
  }

  const items = sources
    .map(s => `<li>${s.source || "unknown"}${s.page ? ` — page ${s.page}` : ""}</li>`)
    .join("");

  sourcesDiv.innerHTML = `
    <div class="sourcesTitle">Sources</div>
    <ul class="sourcesList">${items}</ul>
  `;
}

uploadBtn.onclick = async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Pick a file first.";
    return;
  }

  uploadStatus.textContent = "Uploading + indexing...";
  hasUploaded = false;

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) {
      uploadStatus.textContent = `Upload failed: ${data.error || "unknown error"}`;
      return;
    }

    uploadStatus.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}`;
    hasUploaded = true;
    addMessage(`✅ Uploaded: ${data.filename}`, "assistant");
  } catch (e) {
    uploadStatus.textContent = "Upload failed (network/server error).";
  }
};

sendBtn.onclick = async () => {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";
  renderSources([]);

  if (!hasUploaded) {
    addMessage("⚠️ Upload a PDF first, then ask.", "assistant");
    return;
  }

  addMessage("Thinking...", "thinking");

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: question })
    });

    const data = await res.json();

    // remove "Thinking..."
    const thinking = chat.querySelector(".msg.thinking");
    if (thinking) thinking.remove();

    if (!res.ok) {
      addMessage(`Error: ${data.error || "unknown error"}`, "assistant");
      return;
    }

    addMessage(data.answer, "assistant");
    renderSources(data.sources);
  } catch (e) {
    const thinking = chat.querySelector(".msg.thinking");
    if (thinking) thinking.remove();
    addMessage("Error contacting backend.", "assistant");
  }
};
