from flask import Flask, jsonify, request, redirect, url_for, render_template
import os
import keras
# from keras.models import load_model
import tensorflow as tf
import numpy as np
import json
from keras_preprocessing import image


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


#### Front End ####

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=["POST"])
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

    # savedModel = keras.models.load_model('model/model.h5')
    # pred = savedModel.predict(images)

    with open('model/model.json', 'r') as json_file:
        json_savedModel= json_file.read()#load the model architecture 
    model_j = keras.models.model_from_json(json_savedModel)
    model_j.load_weights('model/model_weights.h5')
    model_j.compile(
        loss='categorical_crossentropy',
        optimizer=tf.keras.optimizers.Adam(),
        metrics=['accuracy']
    )
    pred = model_j.predict(images)

    proba = np.max(pred[0], axis=-1)
    predicted_class = class_names[np.argmax(pred[0], axis=-1)]

    prediction = [proba, predicted_class]
    return prediction


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)