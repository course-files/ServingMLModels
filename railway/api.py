from flask import Flask, request, jsonify
import joblib
import numpy as np

# Create Flask app
app = Flask(__name__)

# Load your trained model
model = joblib.load("./model/decisiontree_classifier_baseline.pkl")

# Health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Customer Churn API is running"}), 200

# Prediction route
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Expect JSON input
        data = request.get_json()

        # Extract features
        monthly_fee = data.get("monthly_fee")
        customer_age = data.get("customer_age")
        support_calls = data.get("support_calls")

        # Validate inputs
        if monthly_fee is None or customer_age is None or support_calls is None:
            return jsonify({"error": "Missing input fields"}), 400

        # Prepare features for prediction
        X = np.array([[monthly_fee, customer_age, support_calls]])

        # Predict
        prediction = model.predict(X)[0]

        # Return result
        return jsonify({"predicted_class": int(prediction)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Only for local testing, Railway will use gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
