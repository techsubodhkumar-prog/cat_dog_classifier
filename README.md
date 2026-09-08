# Cat vs Dog AI Classifier

Professional Flask UI for the uploaded Keras cat-vs-dog model.

## Model details
- Input: 128 x 128 x 3 RGB
- Output: 1 sigmoid value
- Loss: binary crossentropy
- Classes assumed by the app: 0 = Cat, 1 = Dog
- Model file: `cat_dog_model.h5`

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Important
The app assumes that the training labels were:
- 0 -> Cat
- 1 -> Dog

If your training generator used the opposite class order, swap `CLASS_NAMES` in `app.py`.

## Deploy
This project includes a Procfile for Gunicorn-compatible hosting such as Render or Railway.
