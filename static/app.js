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
            console.log(result);

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