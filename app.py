from flask import Flask, jsonify, request, redirect, url_for, render_template
import os
from tensorflow.keras.models import load_model
import numpy as np
import json
from keras_preprocessing import image


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


#### Front End ####

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    msg = "File Terupload di: "+file_path
    pred = classify(file_path)
    return render_template('index.html', filename=file.filename, pred=pred, message=msg)
    

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/'+filename), code=301)



#### API response (Backend) ####

@app.route('/api/predict', methods=["POST"])
def predict():

    if request.method == "POST":
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        pred = classify(file_path)

        prediction = {
            'filename': file.filename,
            'path': file_path,
            'probabilities': str(pred[0]), 
            'prediction': pred[1]
        }
        return jsonify(prediction)
    return jsonify(request='404')
    


#### Model Prediction ####

def convert_image(path):
    img = image.load_img(path, target_size=(150, 150))

    x = image.img_to_array(img)
    x = np.array(x)/255.0
    x = np.expand_dims(x, axis=0)
    return np.vstack([x])


def classify(path):
    images = convert_image(path)

    labels = json.load(open('model/labels_map.json'))
    class_names = list(labels.keys())

    savedModel = load_model('model/model.h5')
    pred = savedModel.predict(images)

    proba = np.max(pred[0], axis=-1)
    predicted_class = class_names[np.argmax(pred[0], axis=-1)]

    prediction = [proba, predicted_class]
    return prediction


if __name__ == "__main__":
    app.run(debug=True)