from flask import Flask, request, jsonify
import tensorflow.lite as tflite
from PIL import Image
import numpy as np
import io

app = Flask(__name__)

# Load TFLite model
interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get model input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess_image(image):
    image = image.resize((224, 224))  # Sesuaikan dengan ukuran model Anda
    image = np.array(image).astype('float32') / 255.0
    return np.expand_dims(image, axis=0)

@app.route('/classify', methods=['POST'])
def classify():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    # Read image
    file = request.files['image']
    image = Image.open(io.BytesIO(file.read()))
    image = preprocess_image(image)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # Convert output to class
    hair_types = ["Curly", "Straight", "Wavy", "Dreadlocks", "Kinky"]  # Sesuaikan dengan dataset Anda
    predicted_index = np.argmax(output_data)
    predicted_label = hair_types[predicted_index]

    return jsonify({"hair_type": predicted_label})

if __name__ == '__main__':
    app.run(debug=True)
