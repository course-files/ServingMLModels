# Publicly Serving the Model for Validation by Domain Experts

There are several free or freemium platforms and techniques that developers can use to demo models (e.g., models saved as .pkl files).

Domain experts can then use these platforms to validate the model and provide the developer with feedback before the model is deployed in a production environment.

Examples:
1. **Hugging Face Spaces – https://huggingface.co/spaces**

    Hugging Face offers a collaborative platform for hosting and sharing machine learning demos. Developers can deploy models easily using Gradio or Streamlit as frontends, with Hugging Face handling the hosting. It is particularly popular in the research and NLP communities because of its integration with the Hugging Face model hub. Domain experts can interact with the model through a simple web UI, making it ideal for quick prototyping and validation.

2. **Streamlit Community Cloud (formerly Streamlit Sharing) – https://share.streamlit.io**

    Streamlit’s official hosting platform allows developers to deploy Python applications directly from a GitHub repository. It is designed to be simple and developer-friendly, with automatic updates whenever the repository changes. Streamlit Sharing is well-suited for lightweight data apps, dashboards, and interactive ML demos. Domain experts can test models via a familiar, user-friendly Streamlit interface.

3. **Render – https://render.com**

    Render is a general-purpose cloud platform for deploying web applications and APIs. Unlike Hugging Face Spaces and Streamlit Sharing, which focus on demos, Render is closer to production-grade deployment. It supports Flask, FastAPI, and Django apps, making it **ideal for exposing a trained model as an API endpoint** (for Postman or integration with other systems). Render offers a free tier (with card verification), enabling developers to test ML APIs before moving to production.

## Hugging Face Spaces using a Gradio App
Overall workflow:
1. Create a Gradio app
2. Deploy the Gradio app to Hugging Face Spaces
3. Domain experts can access the Gradio app via a web interface to test and validate the model's performance

### Step 1: Create a Gradio App (`app.py`)
- Load your model and define a prediction function. 
- Build a Gradio interface.

Sample:
```python
import gradio as gr
import joblib

# Load the model
model = joblib.load('model.pkl')

# Define prediction function
def predict(input_features):
    # Adjust input_features as needed for your model
    prediction = model.predict([input_features])
    return str(prediction[0])

# Create Gradio interface
iface = gr.Interface(
    fn=predict,
    inputs=gr.inputs.Textbox(label="Input Features (comma separated)"),
    outputs="text",
    title="My Model Demo"
)

if __name__ == "__main__":
    iface.launch()
```

- Prepare the `requirements.txt` file
- This contains a scaled down version of the libraries in the original `requirements.txt` file.
Sample:
```text
gradio
numpy
scikit-learn
flask
joblib
```

### Step 2: Deploy the Gradio app to Hugging Face Spaces
- Create a Hugging Face account if you do not have one - [https://huggingface.co/](https://huggingface.co/)
- Create a new Space (right-click on the "Spaces" tab and select "New Space")
- Name the Space
- Select the "Gradio" template
- Select the "Public" visibility

This will create a new repository in your Hugging Face account.
- Upload the `app.py` file in the repository
- Upload the `requirements.txt` file in the repository
- Upload the `.pkl` model and other files as needed to make a prediction

### Step 3: Access the Gradio app via a Web Interface
- Go to the Space URL. This will be in the form of `https://huggingface.co/spaces/<username>/<space_name>`
- The Gradio app will be launched in the browser tab once it automatically builds the Gradio app.
- Enter the input features
- Click the "Submit" button
- View the prediction result
- Share the Space URL with domain experts for validation and feedback. Example: [https://huggingface.co/spaces/course-files/customer-churn-demo](https://huggingface.co/spaces/course-files/customer-churn-demo)

## Streamlit Community Cloud (Streamlit Sharing) using a Streamlit App
Overall workflow:
1. Create a Streamlit app
2. Deploy the Streamlit app to Streamlit Sharing
3. Domain experts can access the Streamlit app via a web interface to test and validate the model's performance

### Step 1: Create a Streamlit App (`app.py`)
- Load your model and define how a prediction will be made. 
- Build a Streamlit interface.

Sample:
```python
import streamlit as st
import joblib
import numpy as np

# Load the model
model = joblib.load('model.pkl')

# Create Streamlit interface
st.set_page_config(
    page_title="Title of the App",
    page_icon="📊",
    layout="centered"
)

st.title("Title of the App")
st.write("Text to guide the user through the app.")

# Sample streamlit input form
with st.form("prediction_form"):
    monthly_fee = st.number_input("Monthly Fee", min_value=0.0, step=1.0)
    customer_age = st.number_input("Customer Age", min_value=0, step=1)
    support_calls = st.number_input("Support Calls", min_value=0, step=1)

    submitted = st.form_submit_button("Predict")

# Sample prediction logic
if submitted:
    X = np.array([[monthly_fee, customer_age, support_calls]])
    prediction = model.predict(X)
    st.success(f"### Predicted Class: {int(prediction[0])}")
```

### Step 2: Deploy the Streamlit app to Streamlit Sharing
- Create a Streamlit account if you do not have one - [https://share.streamlit.io/](https://share.streamlit.io/)
- Create a new app (Click on the "Create App" link at the top right corner)
- Select the "Deploy a public app from GitHub". This assumes that you have a GitHub repository with the Streamlit app.
- Name the app
- Specify the location of the `app.py` file in the GitHub repository
- Specify a custom URL for the app
- Click "Deploy"

### Step 3: Access the Streamlit app via a Web Interface
- Go to the Steamlit Share URL. This will be in the form of `https://<app_name>.streamlit.app/`
- The Streamlit app will be launched in the browser tab once it automatically builds the Streamlit app.
- Enter the input features
- Click the "Predict" button
- View the prediction result
- Share the Streamlit app URL with domain experts for validation and feedback. Example: [https://customer-churn-demo.streamlit.app/](https://customer-churn-demo.streamlit.app/)

## Public API Access via Render

Steps:
1. Prepare your `requirements.txt` file to list all the required dependencies
2. Create your `Procfile` so that render can use it to start your application
3. Prepare your `api.py` file that contains the definition of the endpoints
4. Push your changes to GitHub
5. Go to [https://dashboard.render.com](https://dashboard.render.com)
6. Click + New → Web Service 
7. Connect your GitHub repository that has the code
8. Select the branch (main). Render should auto-detect that you are using Python and Flask.
9. Specify the name of your service
10. Specify the start command as `gunicorn -w 4 -b 0.0.0.0:$PORT api:app` (assuming the Flask app is named `app` and is defined in `api.py`)
11. Select the "Free" plan "For hobby projects"
12. Click "Deploy Web Service"
13. Copy the URL of your service
14. Use the URL + appropriate API endpoint to access your model. **Note:** Accessing the `Render` URL directly via a browswer will give you a `502: Server not found` error.

    Example 1: [https://customer-churn-demo.onrender.com/api/predict_decision_tree_classifier](https://customer-churn-demo.onrender.com/api/predict_decision_tree_classifier)
 
    Example 2: [https://customer-churn-demo.onrender.com/api/predict_decision_tree_regressor](https://customer-churn-demo.onrender.com/api/predict_decision_tree_regressor)

    cURL example 1: 
    ```shell
    curl -X POST https://customer-churn-demo.onrender.com/api/predict_decision_tree_classifier \
      -H "Content-Type: application/json" \
      -d "{\"monthly_fee\": 60, \"customer_age\": 30, \"support_calls\": 1}"
    ```

    cURL example 2: 
    ```shell
    curl -X POST https://customer-churn-demo.onrender.com/api/predict_decision_tree_regressor \
      -H "Content-Type: application/json" \
      -d "{\"CustomerType\": \"Business\",
        \"BranchSubCounty\": \"Kilimani\",
        \"ProductCategoryName\": \"Meat-Based Dishes\",
        \"QuantityOrdered\": 8,
        \"PaymentDate\": \"2025-11-13\"}"
    ```

## Expected Challenges
- Resource limits: On free tiers, memory, CPU, or disk are often significantly constrained. Large models or heavy inference might crash or be slow.
- Cold starts or sleeping: Many free services “sleep” when idle; the first request after idle may suffer delay.
- Public exposure: Many free services only allow public apps (not private), so your model and interface may be accessible by anyone.
- Latency & reliability: Free tiers are not reliable for real-time or production use.
