from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from pathlib import Path
import os


# =========================
# LIMIT TENSORFLOW THREADS
# =========================

tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)


# =========================
# FLASK APP
# =========================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# =========================
# MODEL CONFIGURATION
# =========================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "cat_dog_model.h5"

IMG_SIZE = (128, 128)

CLASS_NAMES = {
    0: "Cat",
    1: "Dog"
}


# =========================
# LOAD MODEL
# =========================

model = None

try:

    print("Loading Cat vs Dog model...")

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )

    print("Cat vs Dog model loaded successfully.")

except Exception as e:

    print("MODEL LOAD ERROR:", repr(e))


# =========================
# IMAGE PREPROCESSING
# =========================

def preprocess_image(file_storage):

    print("Opening uploaded image...")

    image = Image.open(file_storage).convert("RGB")

    print("Original image size:", image.size)

    image = image.resize(IMG_SIZE)

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    image_array /= 255.0

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    print("Processed image shape:", image_array.shape)

    return image_array


# =========================
# HOME
# =========================

@app.route("/")
def index():

    return render_template("index.html")


# =========================
# PREDICTION
# =========================

@app.route("/predict", methods=["POST"])
def predict():

    print("================================")
    print("POST /predict received")
    print("================================")


    # Check model

    if model is None:

        print("ERROR: Model is not loaded.")

        return jsonify({
            "error": "Model is not loaded on the server."
        }), 500


    # Check file

    if "image" not in request.files:

        print("ERROR: No image field.")

        return jsonify({
            "error": "Please select an image."
        }), 400


    image_file = request.files["image"]


    if image_file.filename == "":

        print("ERROR: Empty filename.")

        return jsonify({
            "error": "Please select an image."
        }), 400


    try:

        # =========================
        # PREPROCESS
        # =========================

        image = preprocess_image(image_file)


        print("Starting model prediction...")


        # =========================
        # MODEL INFERENCE
        # =========================

        prediction = model(
            image,
            training=False
        )


        print("Model prediction completed.")


        # Convert TensorFlow tensor to numpy

        probability = float(
            prediction.numpy()[0][0]
        )


        print("Raw probability:", probability)


        # =========================
        # CLASSIFICATION
        # =========================

        if probability >= 0.5:

            predicted_index = 1

        else:

            predicted_index = 0


        predicted_class = CLASS_NAMES[
            predicted_index
        ]


        print("Predicted class:", predicted_class)


        # =========================
        # CONFIDENCE
        # =========================

        if predicted_index == 1:

            confidence = probability

        else:

            confidence = 1.0 - probability


        print(
            "Confidence:",
            round(confidence * 100, 2)
        )


        # =========================
        # RESPONSE
        # =========================

        response = {
            "prediction": predicted_class,
            "confidence": round(
                confidence * 100,
                2
            )
        }


        print("Sending response:", response)


        return jsonify(response)


    except Exception as e:

        print("================================")
        print("PREDICTION ERROR")
        print(repr(e))
        print("================================")


        return jsonify({
            "error": f"Prediction failed: {str(e)}"
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
# START
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