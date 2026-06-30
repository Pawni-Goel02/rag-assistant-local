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
                    `✅ Uploaded: ${result.filename}`;

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