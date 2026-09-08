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

browseBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
        setFile(fileInput.files[0]);
    }
});

["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, event => {
        event.preventDefault();
        dropZone.classList.add("dragging");
    });
});

["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, event => {
        event.preventDefault();
        dropZone.classList.remove("dragging");
    });
});

dropZone.addEventListener("drop", event => {
    const file = event.dataTransfer.files[0];

    if (file) {
        setFile(file);
    }
});

removeBtn.addEventListener("click", reset);

analyzeBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    hideError();

    loadingState.classList.remove("hidden");
    analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        showResult(data);

    } catch (error) {
        showError(error.message);

    } finally {
        loadingState.classList.add("hidden");
        analyzeBtn.disabled = false;
    }
});


function setFile(file) {
    hideError();

    const allowed = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowed.includes(file.type)) {
        showError("Please upload a JPG, PNG or WEBP image.");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError("Image is too large. Maximum size is 10 MB.");
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

    reader.readAsDataURL(file);
}


function showResult(data) {
    emptyResult.classList.add("hidden");
    resultContent.classList.remove("hidden");

    const isDog = data.prediction === "Dog";

    predictionIcon.textContent = isDog ? "🐶" : "🐱";
    predictionText.textContent = data.prediction;
}


function reset() {
    selectedFile = null;

    fileInput.value = "";

    previewImage.removeAttribute("src");

    previewArea.classList.add("hidden");
    dropZone.classList.remove("hidden");

    resultContent.classList.add("hidden");
    emptyResult.classList.remove("hidden");

    hideError();
}


function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


function hideError() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}


function formatSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}