
# Import necessary libraries
import os
import numpy as np
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask application
superkart_api = Flask("SuperKart")

# Load the trained model from the same folder as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "superkart_model.joblib")

model = joblib.load(MODEL_PATH)

# Define the expected input features
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category"
]

# Home endpoint
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart System"

# Endpoint for single product prediction
@superkart_api.post("/v1/predict")
def predict_sales():

    try:
        # Get JSON data from request
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Please provide a valid JSON object"
            }), 400

        # Check for missing features
        missing = [col for col in FEATURES if col not in data]

        if missing:
            return jsonify({
                "error": "Missing required features",
                "missing_features": missing
            }), 400

        # Extract features
        sample = {col: data[col] for col in FEATURES}

        # Convert to DataFrame
        input_data = pd.DataFrame([sample])

        # Predict sales
        prediction = float(model.predict(input_data)[0])

        # Return JSON response
        return jsonify({
            "Sales": round(prediction, 2)
        })

    except (ValueError, TypeError, KeyError) as e:
        return jsonify({"error": str(e)}), 400

# Endpoint for batch predictions
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():

    try:
        # Check whether a file was uploaded
        if "file" not in request.files:
            return jsonify({
                "error": "No CSV file uploaded"
            }), 400

        file = request.files["file"]

        # Read uploaded CSV
        input_data = pd.read_csv(file)

        # Check required features
        missing = [
            col for col in FEATURES
            if col not in input_data.columns
        ]

        if missing:
            return jsonify({
                "error": "Missing required columns",
                "missing_columns": missing
            }), 400

        # Generate predictions
        predictions = model.predict(input_data[FEATURES])

        # Return predictions indexed by row
        output_dict = {
            str(i): round(float(pred), 2)
            for i, pred in enumerate(predictions)
        }

        return jsonify(output_dict)

    except (ValueError, TypeError, pd.errors.ParserError) as e:
        return jsonify({"error": str(e)}), 400

# Run Flask application
if __name__ == "__main__":
    superkart_api.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
