function stringifyError(err) {
  if (!err) return "Unknown error";
  if (typeof err === "string") return err;
  return JSON.stringify(err, null, 2);
}


const chat = document.getElementById("chat");
const input = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const fileList = document.getElementById("fileList");
const refreshFilesBtn = document.getElementById("refreshFilesBtn");

const sourcesDiv = document.getElementById("sources");
const crossToggle = document.getElementById("crossDocumentToggle");

let selectedFile = null;

/* ---------- UI helpers ---------- */
function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.innerHTML = marked.parse(text);

  if (window.MathJax) MathJax.typesetPromise([div]);

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function renderSources(sources) {
  if (!sources || sources.length === 0) {
    sourcesDiv.innerHTML = "";
    return;
  }

  const items = sources
    .map((s) => `<li>${s.source} — page ${s.page ?? "?"}</li>`)
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

    files.forEach((name) => {
      const li = document.createElement("li");
      li.textContent = name;

      li.onclick = () => {
        selectedFile = name;
        document.querySelectorAll("#fileList li").forEach((el) => el.classList.remove("active"));
        li.classList.add("active");
      };

      fileList.appendChild(li);
    });

    if (selectedFile) {
      [...fileList.querySelectorAll("li")].forEach((li) => {
        if (li.textContent === selectedFile) li.classList.add("active");
      });
    }
  } catch (e) {
    console.error(e);
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
    const data = await res.json();

    if (!res.ok || data.status === "error") {
      addMessage(
        `❌ Backend error:\n\`\`\`json\n${stringifyError(data.error)}\n\`\`\``,
        "assistant"
      );
      return;
    }
    

    uploadStatus.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}`;
    addMessage(`✅ Uploaded: ${data.filename}`, "assistant");

    selectedFile = data.filename;
    await loadFiles();
  } catch (e) {
    console.error(e);
    uploadStatus.textContent = "Upload failed (server error).";
    addMessage(`❌ Backend error:\n\`\`\`json\n${stringifyError(data.error)}\n\`\`\``, "assistant");

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

  const form = new FormData();
  form.append("question", question);
  form.append("source", selectedFile);
  form.append(
    "cross_document",
    document.getElementById("crossDocumentToggle").checked
  );

  try {
    const res = await fetch("/query", {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    thinking.remove();

    if (!res.ok) {
      addMessage(`❌ ${data.detail}`, "assistant");
      return;
    }

    addMessage(data.answer, "assistant");
    renderSources(data.sources);

  } catch (e) {
    thinking.remove();
    addMessage("❌ Server error", "assistant");
  }
});
