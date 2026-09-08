@app.post("/predict")
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Please select an image."}), 400

    image_file = request.files["image"]

    if not image_file.filename:
        return jsonify({"error": "Please select an image."}), 400

    try:
        print("Prediction request received")

        image = preprocess_image(image_file)

        print("Image preprocessed:", image.shape)

        prediction = model.predict(image, verbose=0)

        print("Raw prediction:", prediction)

        probability = float(prediction[0][0])

        predicted_index = 1 if probability >= 0.5 else 0
        confidence = probability if predicted_index == 1 else 1.0 - probability

        result = {
            "prediction": CLASS_NAMES[predicted_index],
            "confidence": round(confidence * 100, 2),
            "dog_probability": round(probability * 100, 2),
            "cat_probability": round((1.0 - probability) * 100, 2)
        }

        print("Prediction result:", result)

        return jsonify(result), 200

    except Exception as exc:
        print("PREDICTION ERROR:", repr(exc))

        return jsonify({
            "error": str(exc)
        }), 500