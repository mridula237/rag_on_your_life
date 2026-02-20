let activeFile = null;

/* ===========================
   Upload PDF
=========================== */

document.getElementById("uploadBtn").addEventListener("click", uploadPDF);

async function uploadPDF() {
    const fileInput = document.getElementById("fileInput");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {
        status.textContent = "Select a file first.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    status.textContent = "Uploading...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        activeFile = data.filename;

        await refreshFileList();
        highlightActiveFile(activeFile);

        status.textContent = `Uploaded ${data.filename} (${data.chunks_indexed} chunks)`;
        fileInput.value = "";
    } catch (err) {
        console.error(err);
        status.textContent = "Upload failed.";
    }
}

/* ===========================
   File List Handling
=========================== */

document.getElementById("refreshFilesBtn").addEventListener("click", refreshFileList);

async function refreshFileList() {
    try {
        const response = await fetch("/files");
        const data = await response.json();

        const fileList = document.getElementById("fileList");
        fileList.innerHTML = "";

        data.files.forEach(filename => {
            const li = document.createElement("li");
            li.textContent = filename;
            li.className = "fileItem";

            li.onclick = () => {
                activeFile = filename;
                highlightActiveFile(filename);
            };

            fileList.appendChild(li);
        });

    } catch (err) {
        console.error(err);
    }
}

function highlightActiveFile(filename) {
    const items = document.querySelectorAll(".fileItem");

    items.forEach(item => {
        item.classList.remove("activeFile");

        if (item.textContent === filename) {
            item.classList.add("activeFile");
        }
    });
}

/* ===========================
   Ask Question
=========================== */

document.getElementById("sendBtn").addEventListener("click", askQuestion);

async function askQuestion() {
    const questionInput = document.getElementById("questionInput");
    const chat = document.getElementById("chat");
    const sourcesList = document.getElementById("sources");
    const crossDocument = document.getElementById("crossDocumentToggle").checked;

    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message
    appendMessage("You", question);

    questionInput.value = "";

    appendMessage("AI", "Thinking...");

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: question,
                search_all: crossDocument
            })
        });

        const data = await response.json();

        // Replace "Thinking..."
        replaceLastAIMessage(data.answer || "No response.");

        // Render sources
        sourcesList.innerHTML = "";
        if (data.sources) {
            data.sources.forEach(src => {
                const li = document.createElement("li");
                li.textContent = `${src.source} — page ${src.page}`;
                sourcesList.appendChild(li);
            });
        }

    } catch (err) {
        console.error(err);
        replaceLastAIMessage("Error processing request.");
    }
}

/* ===========================
   Chat Helpers
=========================== */

function appendMessage(sender, text) {
    const chat = document.getElementById("chat");

    const messageDiv = document.createElement("div");
    messageDiv.className = sender === "You" ? "message user" : "message ai";

    messageDiv.innerHTML = `<strong>${sender}:</strong><br>${text}`;

    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}

function replaceLastAIMessage(text) {
    const messages = document.querySelectorAll(".message.ai");
    if (messages.length === 0) return;

    messages[messages.length - 1].innerHTML = `<strong>AI:</strong><br>${text}`;
}

/* ===========================
   Initialize
=========================== */

refreshFileList();