const chat = document.getElementById("chat");
const input = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const fileList = document.getElementById("fileList");
const refreshFilesBtn = document.getElementById("refreshFilesBtn");

const sourcesDiv = document.getElementById("sources");

/* ---------- UI helpers ---------- */

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
    .map(s => `<li>${s.source} — page ${s.page ?? "?"}</li>`)
    .join("");

  sourcesDiv.innerHTML = `
    <div class="sourcesTitle">Sources</div>
    <ul class="sourcesList">${items}</ul>
  `;
}

/* ---------- Files ---------- */

async function loadFiles() {
  try {
    const res = await fetch("/files");
    const files = await res.json();

    fileList.innerHTML = "";
    files.forEach(name => {
      const li = document.createElement("li");
      li.textContent = name;
      fileList.appendChild(li);
    });
  } catch (e) {
    console.error("Failed to load files:", e);
  }
}

refreshFilesBtn.addEventListener("click", loadFiles);

/* ---------- Upload ---------- */

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Pick a PDF first.";
    return;
  }

  uploadStatus.textContent = "Uploading + indexing...";
  renderSources([]);

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: form });
    const text = await res.text(); // read raw first
    const data = JSON.parse(text);

    if (!res.ok) {
      uploadStatus.textContent = `Upload failed: ${data.error || text}`;
      return;
    }

    uploadStatus.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}`;
    addMessage(`✅ Uploaded: ${data.filename}`, "assistant");
    await loadFiles();
  } catch (e) {
    console.error(e);
    uploadStatus.textContent = "Upload failed (server error).";
  }
});

/* ---------- Ask ---------- */

sendBtn.addEventListener("click", async () => {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";
  renderSources([]);

  const thinking = document.createElement("div");
  thinking.className = "msg thinking";
  thinking.textContent = "Thinking...";
  chat.appendChild(thinking);
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: question   // ✅ matches backend
      })
    });

    const raw = await res.text(); // IMPORTANT
    let data;

    try {
      data = JSON.parse(raw);
    } catch {
      throw new Error(`Invalid JSON from backend:\n${raw}`);
    }

    thinking.remove();

    if (!res.ok) {
      addMessage(`❌ Backend error: ${data.error || raw}`, "assistant");
      return;
    }

    addMessage(data.answer, "assistant");
    renderSources(data.sources);

  } catch (e) {
    thinking.remove();
    console.error(e);
    addMessage(`❌ ${e.message}`, "assistant");
  }
});

loadFiles();
