const sendButton =
    document.getElementById("send-btn");

const messageInput =
    document.getElementById("message-input");

const chatWindow =
    document.getElementById("chat-window");

const documentList =
    document.getElementById("document-list");

const docCount =
    document.getElementById("doc-count");

const uploadButton =
    document.getElementById("upload-btn");

const fileInput =
    document.getElementById("file-input");

const fileNameLabel =
    document.getElementById("file-name");

const uploadStatus =
    document.getElementById("upload-status");

const newChatButton =
    document.getElementById("new-chat-btn");

const clearDocsButton =
    document.getElementById("clear-docs-btn");

const urlButton =
    document.getElementById("url-btn");

const urlInput =
    document.getElementById("url-input");

// Small inline SVG used for every indexed-document row
const DOC_ICON = `
    <svg class="doc-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke-linejoin="round"/>
        <path d="M14 2v6h6" stroke-linejoin="round"/>
    </svg>
`;

function escapeHtml(value) {

    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}

function renderDocumentList(documents) {

    docCount.textContent = documents.length
        ? documents.length
        : "";

    if (documents.length === 0) {

        documentList.innerHTML =
            `<p class="empty-state">No documents yet — add a file or URL to get started.</p>`;

        return;
    }

    documentList.innerHTML = documents.map(doc => `
        <div class="doc-card">
            ${DOC_ICON}
            <span class="doc-name" title="${escapeHtml(doc)}">${escapeHtml(doc)}</span>
        </div>
    `).join("");
}

async function loadDocuments() {

    try {

        const response = await fetch("/documents");
        const result = await response.json();

        renderDocumentList(result.documents || []);

    } catch (error) {

        console.error("Failed to load documents:", error);
    }
}

loadDocuments();

// ---------- File selection preview ----------
fileInput.addEventListener("change", () => {

    fileNameLabel.textContent =
        fileInput.files[0]
            ? fileInput.files[0].name
            : "No file selected";
});

// ---------- File upload ----------
uploadButton.addEventListener(
    "click",
    async () => {

        const file =
            fileInput.files[0];

        if (!file) {

            uploadStatus.innerHTML =
                "Select a file first";

            return;
        }

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );

        uploadButton.disabled = true;
        const originalButtonText = uploadButton.textContent;
        uploadButton.textContent = "Uploading...";

        uploadStatus.innerHTML =
            `<span class="spinner"></span> Uploading &amp; indexing "${escapeHtml(file.name)}"...`;

        try {

            const response =
                await fetch(
                    "/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            if (!response.ok) {

                const error = await response.json().catch(() => ({}));
                uploadStatus.innerHTML =
                    `❌ ${escapeHtml(error.detail || "Upload failed")}`;
                return;
            }

            const result = await response.json();

            uploadStatus.innerHTML =
                `✅ Uploaded ${escapeHtml(result.filename)} — indexed ${result.chunks} chunks`;

            fileInput.value = "";
            fileNameLabel.textContent = "No file selected";

            loadDocuments();

        } catch (error) {

            uploadStatus.innerHTML =
                "❌ Upload failed — check your connection and try again";

        } finally {

            uploadButton.disabled = false;
            uploadButton.textContent = originalButtonText;
        }
    }
);

// ---------- URL ingestion ----------
async function submitUrl() {

    const url =
        urlInput.value.trim();

    if (!url)
        return;

    urlButton.disabled = true;
    const originalButtonText = urlButton.textContent;
    urlButton.textContent = "Indexing...";

    uploadStatus.innerHTML =
        `<span class="spinner"></span> Fetching &amp; indexing URL...`;

    try {

        const response =
            await fetch(
                "/upload-url",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ url })
                }
            );

        const result =
            await response.json();

        if (response.ok) {

            uploadStatus.innerHTML =
                `✅ Indexed URL — ${result.chunks} chunks`;

            urlInput.value = "";
            loadDocuments();

        } else {

            uploadStatus.innerHTML =
                `❌ ${escapeHtml(result.detail || "Failed to index URL")}`;
        }

    } catch (error) {

        uploadStatus.innerHTML =
            "❌ Failed to index URL — check your connection and try again";

    } finally {

        urlButton.disabled = false;
        urlButton.textContent = originalButtonText;
    }
}

urlButton.addEventListener("click", submitUrl);

urlInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {
        event.preventDefault();
        submitUrl();
    }
});

// ---------- Chat ----------
function renderSources(container, sources) {

    if (!sources || sources.length === 0)
        return;

    const block = document.createElement("div");
    block.className = "sources-block";

    const label = document.createElement("span");
    label.className = "sources-label";
    label.textContent = "Grounded in";
    block.appendChild(label);

    const row = document.createElement("div");
    row.className = "stamp-row";

    sources.forEach(source => {

        const stamp = document.createElement("span");
        stamp.className = "stamp";
        stamp.innerHTML =
            `${escapeHtml(source.source)} <span class="stamp-page">· p.${escapeHtml(String(source.page))}</span>`;

        row.appendChild(stamp);
    });

    block.appendChild(row);
    container.appendChild(block);
}

function autoResizeInput() {

    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 140) + "px";
}

messageInput.addEventListener("input", autoResizeInput);

messageInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {

    const question = messageInput.value.trim();

    if (!question) {
        return;
    }

    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.innerHTML =
        `<strong>You</strong>${escapeHtml(question)}`;
    chatWindow.appendChild(userDiv);

    messageInput.value = "";
    autoResizeInput();
    sendButton.disabled = true;

    chatWindow.scrollTop = chatWindow.scrollHeight;

    let response;

    try {

        response = await fetch(
            "/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            }
        );

    } catch (error) {

        const errorDiv = document.createElement("div");
        errorDiv.className = "assistant-message";
        errorDiv.innerHTML =
            `<strong>Assistant</strong>❌ Could not reach the server. Please try again.`;
        chatWindow.appendChild(errorDiv);

        sendButton.disabled = false;
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    const assistantDiv = document.createElement("div");
    assistantDiv.className = "assistant-message";

    const answerSpan = document.createElement("span");
    answerSpan.className = "answer-text";

    assistantDiv.innerHTML = "<strong>Assistant</strong>";
    assistantDiv.appendChild(answerSpan);
    answerSpan.innerHTML =
        `<span class="typing-indicator"><span></span><span></span><span></span></span>`;

    chatWindow.appendChild(assistantDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    let buffer = "";
    let receivedFirstToken = false;
    let answerText = "";

    while (true) {

        const { done, value } =
            await reader.read();

        if (done) break;

        buffer += decoder.decode(value);

        const events = buffer.split("\n\n");

        buffer = events.pop();

        for (const event of events) {

            if (!event.startsWith("data: "))
                continue;

            const json =
                JSON.parse(
                    event.replace("data: ", "")
                );

            if (json.type === "token") {

                if (!receivedFirstToken) {

                    answerSpan.innerHTML = "";
                    receivedFirstToken = true;
                }

                answerText += json.data;
                answerSpan.textContent = answerText;
            }

            if (json.type === "sources") {

                renderSources(assistantDiv, json.data);
            }
        }

        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    sendButton.disabled = false;
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

sendButton.addEventListener("click", sendMessage);

// ---------- New chat / clear documents ----------
newChatButton.addEventListener(
    "click",
    async () => {

        await fetch(
            "/chat/reset",
            {
                method: "POST"
            }
        );

        chatWindow.innerHTML = `
            <div class="assistant-message welcome-message">
                <strong>Assistant</strong>
                Hello! Add a document or URL on the left, then ask me anything about it.
                I'll only answer from what's indexed — if it's not in there, I'll say so.
            </div>
        `;
    }
);

clearDocsButton.addEventListener(
    "click",
    async () => {

        await fetch(
            "/documents/clear",
            {
                method: "POST"
            }
        );

        renderDocumentList([]);

        uploadStatus.innerHTML = "";

        fileInput.value = "";
        fileNameLabel.textContent = "No file selected";
    }
);