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
                "Upload failed";
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

        const response = await fetch(
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

        const reader = response.body.getReader();

const decoder = new TextDecoder();

let assistantDiv = document.createElement("div");

assistantDiv.className = "assistant-message";

assistantDiv.innerHTML =
    "<strong>Assistant:</strong><br>";

chatWindow.appendChild(assistantDiv);

let buffer = "";

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

}

        messageInput.value = "";

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