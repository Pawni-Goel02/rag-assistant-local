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

            const result =
                await response.json();


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

        const result = await response.json();

        chatWindow.innerHTML += `
            <div class="assistant-message">
                <strong>Assistant:</strong><br>
                ${result.answer}
            </div>
        `;

        messageInput.value = "";

        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
);