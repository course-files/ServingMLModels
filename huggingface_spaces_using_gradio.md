# Publicly Serving the Model for Validation by Domain Experts

There are several free or freemium platforms and techniques that developers can use to demo models (e.g., models saved as .pkl files).

Domain experts can then use these platforms to validate the model and provide the developer with feedback before deploying the model in a production environment.

Examples:
1. **Hugging Face Spaces** - [https://huggingface.co/spaces](https://huggingface.co/spaces): Hugging Face provides a platform called "Spaces" where developers can host machine learning models and applications. It supports various frameworks like Gradio and Streamlit, making it easy to create interactive demos. Domain experts can access these demos via a web interface to test and validate the model's performance.
2. **Streamlit Sharing** - [https://streamlit.io/](https://streamlit.io/): Streamlit provides a platform called "Sharing" where developers can host machine learning models and applications. It supports various frameworks like Gradio and Streamlit, making it easy to create interactive demos. Domain experts can also access these demos via a web interface to test and validate the model's performance.
3. **Koyeb** - [https://koyeb.com/](https://koyeb.com/)
4. **Heroku** - [https://www.heroku.com/](https://www.heroku.com/)

## Hugging Face Spaces using Gradio
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

## Expected Challenges
- Resource limits: On free tiers, memory, CPU, or disk are often significantly constrained. Large models or heavy inference might crash or be slow.
- Cold starts or sleeping: Many free services “sleep” when idle; the first request after idle may suffer delay.
- Public exposure: Many free services only allow public apps (not private), so your model and interface may be accessible by anyone.
- Latency & reliability: Free tiers are not reliable for real-time or production use.