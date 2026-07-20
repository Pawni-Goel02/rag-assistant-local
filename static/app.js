const sendButton =
    document.getElementById("send-btn");

const messageInput =
    document.getElementById("message-input");

const chatWindow =
    document.getElementById("chat-window");

const documentList =
    document.getElementById("document-list");
console.log("APP JS LOADED");
const uploadButton =
    document.getElementById("upload-btn");

const fileInput =
    document.getElementById("file-input");

const uploadStatus =
    document.getElementById("upload-status");

const newChatButton =
    document.getElementById("new-chat-btn");

const clearDocsButton =
    document.getElementById("clear-docs-btn");
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
            `<span class="spinner"></span> Uploading & indexing "${file.name}"...`;

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
    const error = await response.text();
    console.error(error);
    uploadStatus.innerHTML = "❌ Upload failed";
    return;
}

const result = await response.json();


            if (response.ok) {

                uploadStatus.innerHTML =
                    `✅ Uploaded: ${result.filename}<br>
                    Indexed ${result.chunks} chunks`;

                documentList.innerHTML = `
                    <div class="card p-2 mt-2">
                        📄 ${result.filename}
                    </div>
                `;


            } else {

                uploadStatus.innerHTML =
                    `❌ ${result.detail}`;
            }

        } catch (error) {

            uploadStatus.innerHTML =
                "❌ Upload failed";
        } finally {

            uploadButton.disabled = false;
            uploadButton.textContent = originalButtonText;
        }
    }
);

sendButton.addEventListener(
    "click",
    async () => {

        const question = messageInput.value.trim();

        if (!question) {
            return;
        }

        chatWindow.innerHTML += `
            <div class="user-message">
                <strong>You:</strong><br>
                ${question}
            </div>
        `;

        messageInput.value = "";
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

            chatWindow.innerHTML += `
                <div class="assistant-message">
                    ❌ Could not reach the server. Please try again.
                </div>
            `;

            sendButton.disabled = false;
            return;
        }

        const reader = response.body.getReader();

const decoder = new TextDecoder();

let assistantDiv = document.createElement("div");

assistantDiv.className = "assistant-message";

assistantDiv.innerHTML =
    `<strong>Assistant:</strong><br><span class="typing-indicator"><span></span><span></span><span></span></span>`;

chatWindow.appendChild(assistantDiv);

chatWindow.scrollTop = chatWindow.scrollHeight;

let buffer = "";
let receivedFirstToken = false;

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

                // First token arrived - clear the typing indicator
                assistantDiv.innerHTML =
                    "<strong>Assistant:</strong><br>";

                receivedFirstToken = true;
            }

            assistantDiv.innerHTML +=
                json.data;

        }

        if (json.type === "sources") {

            assistantDiv.innerHTML +=
                "<br><br><b>📄 Sources</b><br>";

            json.data.forEach(source => {

                assistantDiv.innerHTML +=
                    `${source.source} (Page ${source.page})<br>`;

            });

        }

    }

    chatWindow.scrollTop = chatWindow.scrollHeight;

}

        sendButton.disabled = false;

        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
);

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
            <div class="assistant-message">
                Hello! Upload documents and ask questions.
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

        documentList.innerHTML =
            "No documents yet";

        uploadStatus.innerHTML = "";

        fileInput.value = "";

    }
);

async function loadDocuments() {

    const response = await fetch("/documents");

    const result = await response.json();

    if (result.documents.length === 0) {

        documentList.innerHTML =
            "No documents yet";

        return;
    }

    documentList.innerHTML = "";

    result.documents.forEach(doc => {

        documentList.innerHTML += `
            <div class="card p-2 mt-2">
                📄 ${doc}
            </div>
        `;

    });

}
loadDocuments();

const urlButton =
    document.getElementById("url-btn");

const urlInput =
    document.getElementById("url-input");

urlButton.addEventListener(
    "click",
    async () => {

        const url =
            urlInput.value.trim();

        if (!url)
            return;

        urlButton.disabled = true;
        const originalButtonText = urlButton.textContent;
        urlButton.textContent = "Indexing...";

        uploadStatus.innerHTML =
            `<span class="spinner"></span> Fetching & indexing URL...`;

        try {

            const response =
                await fetch(
                    "/upload-url",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                            "application/json"
                        },
                        body: JSON.stringify({
                            url
                        })
                    }
                );

            const result =
                await response.json();

            if (response.ok) {

                uploadStatus.innerHTML =
                    `✅ Indexed URL<br>
                    ${result.chunks} chunks`;

                loadDocuments();

            } else {

                uploadStatus.innerHTML =
                    `❌ ${result.detail || "Failed"}`;
            }

        } catch (error) {

            uploadStatus.innerHTML =
                "❌ Failed to index URL";

        } finally {

            urlButton.disabled = false;
            urlButton.textContent = originalButtonText;
        }

    }
);