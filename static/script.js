const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const previewArea = document.getElementById("previewArea");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeBtn = document.getElementById("removeBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingState = document.getElementById("loadingState");
const errorBox = document.getElementById("errorBox");

const emptyResult = document.getElementById("emptyResult");
const resultContent = document.getElementById("resultContent");
const predictionIcon = document.getElementById("predictionIcon");
const predictionText = document.getElementById("predictionText");

let selectedFile = null;


/* =========================
   BROWSE IMAGE
========================= */

browseBtn.addEventListener("click", () => {
    fileInput.click();
});


fileInput.addEventListener("change", () => {

    if (fileInput.files.length) {
        setFile(fileInput.files[0]);
    }

});


/* =========================
   DRAG & DROP
========================= */

["dragenter", "dragover"].forEach(eventName => {

    dropZone.addEventListener(eventName, event => {

        event.preventDefault();
        event.stopPropagation();

        dropZone.classList.add("dragging");

    });

});


["dragleave", "drop"].forEach(eventName => {

    dropZone.addEventListener(eventName, event => {

        event.preventDefault();
        event.stopPropagation();

        dropZone.classList.remove("dragging");

    });

});


dropZone.addEventListener("drop", event => {

    const file = event.dataTransfer.files[0];

    if (file) {
        setFile(file);
    }

});


/* =========================
   REMOVE IMAGE
========================= */

removeBtn.addEventListener("click", reset);


/* =========================
   ANALYZE IMAGE
========================= */

analyzeBtn.addEventListener("click", async () => {

    if (!selectedFile) {
        showError("Please select an image first.");
        return;
    }

    hideError();

    loadingState.classList.remove("hidden");
    analyzeBtn.disabled = true;

    const formData = new FormData();

    formData.append("image", selectedFile);

    try {

        console.log("Sending image to /predict...");
        console.log("File:", selectedFile.name);
        console.log("Size:", selectedFile.size);
        console.log("Type:", selectedFile.type);

        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        console.log("Response status:", response.status);
        console.log("Response OK:", response.ok);

        const responseText = await response.text();

        console.log("Server response:", responseText);

        let data;

        try {

            data = JSON.parse(responseText);

        } catch (error) {

            throw new Error(
                `Server returned an invalid response (${response.status}).`
            );

        }


        if (!response.ok) {

            throw new Error(
                data.error || `Server error (${response.status}).`
            );

        }


        if (!data.prediction) {

            throw new Error(
                "Prediction was not returned by the server."
            );

        }


        showResult(data);

    } catch (error) {

        console.error("Prediction error:", error);

        showError(
            error.message || "Prediction failed. Please try again."
        );

    } finally {

        loadingState.classList.add("hidden");

        analyzeBtn.disabled = false;

    }

});


/* =========================
   SET FILE
========================= */

function setFile(file) {

    hideError();

    const allowed = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];


    if (!allowed.includes(file.type)) {

        showError(
            "Please upload a JPG, PNG or WEBP image."
        );

        return;

    }


    if (file.size > 10 * 1024 * 1024) {

        showError(
            "Image is too large. Maximum size is 10 MB."
        );

        return;

    }


    selectedFile = file;


    const reader = new FileReader();


    reader.onload = event => {

        previewImage.src = event.target.result;

        fileName.textContent = file.name;

        fileSize.textContent = formatSize(file.size);

        dropZone.classList.add("hidden");

        previewArea.classList.remove("hidden");

    };


    reader.onerror = () => {

        showError(
            "Unable to read the selected image."
        );

    };


    reader.readAsDataURL(file);

}


/* =========================
   SHOW RESULT
========================= */

function showResult(data) {

    emptyResult.classList.add("hidden");

    resultContent.classList.remove("hidden");


    const prediction = String(data.prediction).trim();

    const isDog = prediction.toLowerCase() === "dog";


    predictionIcon.textContent = isDog ? "🐶" : "🐱";

    predictionText.textContent = prediction;

}


/* =========================
   RESET
========================= */

function reset() {

    selectedFile = null;

    fileInput.value = "";

    previewImage.removeAttribute("src");

    fileName.textContent = "image.jpg";

    fileSize.textContent = "0 KB";

    previewArea.classList.add("hidden");

    dropZone.classList.remove("hidden");

    resultContent.classList.add("hidden");

    emptyResult.classList.remove("hidden");

    hideError();

}


/* =========================
   SHOW ERROR
========================= */

function showError(message) {

    errorBox.textContent = message;

    errorBox.classList.remove("hidden");

}


/* =========================
   HIDE ERROR
========================= */

function hideError() {

    errorBox.classList.add("hidden");

    errorBox.textContent = "";

}


/* =========================
   FORMAT FILE SIZE
========================= */

function formatSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (bytes < 1024 * 1024) {

        return `${(bytes / 1024).toFixed(1)} KB`;

    }


    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

}