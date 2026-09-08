from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from pathlib import Path
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "cat_dog_model.h5"

# Your model uses a 128x128x3 input and a single sigmoid output.
IMG_SIZE = (128, 128)

# IMPORTANT:
# This assumes sigmoid 0 -> Cat and sigmoid 1 -> Dog.
# If your training labels were reversed, swap these two names.
CLASS_NAMES = {
    0: "Cat",
    1: "Dog"
}

model = tf.keras.models.load_model(MODEL_PATH, compile=False)


def preprocess_image(file_storage):
    image = Image.open(file_storage).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.asarray(image, dtype=np.float32) / 255.0
    return np.expand_dims(image_array, axis=0)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/predict")
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Please select an image."}), 400

    image_file = request.files["image"]

    if not image_file.filename:
        return jsonify({"error": "Please select an image."}), 400

    try:
        image = preprocess_image(image_file)
        probability = float(model.predict(image, verbose=0)[0][0])

        predicted_index = 1 if probability >= 0.5 else 0
        confidence = probability if predicted_index == 1 else 1.0 - probability

        return jsonify({
            "prediction": CLASS_NAMES[predicted_index],
            "confidence": round(confidence * 100, 2),
            "dog_probability": round(probability * 100, 2),
            "cat_probability": round((1.0 - probability) * 100, 2)
        })

    except Exception as exc:
        return jsonify({"error": f"Could not analyze the image: {str(exc)}"}), 500


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Image is too large. Maximum size is 10 MB."}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
