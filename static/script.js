const chat = document.getElementById("chat");
const input = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const fileList = document.getElementById("fileList");
const refreshFilesBtn = document.getElementById("refreshFilesBtn");

const sourcesDiv = document.getElementById("sources");

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

async function loadFiles() {
  const res = await fetch("/files");
  const files = await res.json();

  fileList.innerHTML = "";
  files.forEach(name => {
    const li = document.createElement("li");
    li.textContent = name;
    fileList.appendChild(li);
  });
}

refreshFilesBtn.addEventListener("click", loadFiles);

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
    const data = await res.json();

    if (!res.ok) {
      uploadStatus.textContent = `Upload failed: ${data.error || "unknown error"}`;
      return;
    }

    uploadStatus.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}`;
    addMessage(`✅ Uploaded: ${data.filename}`, "assistant");
    await loadFiles();
  } catch (e) {
    uploadStatus.textContent = "Upload failed (network/server error).";
  }
});

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
      body: JSON.stringify({ query: question })
    });

    const data = await res.json();
    thinking.remove();

    if (!res.ok) {
      addMessage(`Error: ${data.error || "unknown error"}`, "assistant");
      return;
    }

    addMessage(data.answer, "assistant");
    renderSources(data.sources);
  } catch (e) {
    thinking.remove();
    addMessage("Error contacting backend.", "assistant");
  }
});

loadFiles();
