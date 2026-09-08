from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from pathlib import Path
import os


# =========================
# FLASK APP
# =========================

app = Flask(__name__)

# Maximum upload size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# =========================
# MODEL CONFIGURATION
# =========================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "cat_dog_model.h5"

IMG_SIZE = (128, 128)

# Class mapping
# 0 = Cat
# 1 = Dog
CLASS_NAMES = {
    0: "Cat",
    1: "Dog"
}


# =========================
# LOAD MODEL
# =========================

try:

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )

    print("Cat vs Dog model loaded successfully.")

except Exception as e:

    print("ERROR loading model:", e)
    model = None


# =========================
# IMAGE PREPROCESSING
# =========================

def preprocess_image(file_storage):

    image = Image.open(file_storage).convert("RGB")

    # Resize to model input size
    image = image.resize(IMG_SIZE)

    # Convert image to numpy array
    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    # Normalize pixel values
    image_array = image_array / 255.0

    # Add batch dimension
    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():

    return render_template("index.html")


# =========================
# PREDICTION API
# =========================

@app.post("/predict")
def predict():

    # Check model
    if model is None:

        return jsonify({
            "error": "Model could not be loaded on the server."
        }), 500


    # Check uploaded file
    if "image" not in request.files:

        return jsonify({
            "error": "Please select an image."
        }), 400


    image_file = request.files["image"]


    # Check filename
    if not image_file.filename:

        return jsonify({
            "error": "Please select an image."
        }), 400


    try:

        # Preprocess image
        image = preprocess_image(image_file)


        # Make prediction
        prediction = model.predict(
            image,
            verbose=0
        )


        # Convert prediction to float
        probability = float(prediction[0][0])


        # Determine class
        if probability >= 0.5:

            predicted_index = 1

        else:

            predicted_index = 0


        predicted_class = CLASS_NAMES[predicted_index]


        # Confidence
        if predicted_index == 1:

            confidence = probability

        else:

            confidence = 1.0 - probability


        # Return JSON
        return jsonify({

            "prediction": predicted_class,

            "confidence": round(
                confidence * 100,
                2
            )

        })


    except Exception as e:

        print("Prediction error:", e)

        return jsonify({

            "error": f"Could not analyze the image: {str(e)}"

        }), 500


# =========================
# FILE TOO LARGE
# =========================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "error": "Image is too large. Maximum size is 10 MB."

    }), 413


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )