# Serving Machine Learning Models through REST APIs using Flask in Python

| Key              | Value                                                                                                                                                                                                                                                                                     |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Course Codes** | BBT 4206                                                                                                                                                                                                                                                                                  |
| **Course Names** | BBT 4206: Business Intelligence II (Week 4-6 of 13)                                                                                                                                                                                                                                       |
| **Semester**     | January to April 2026                                                                                                                                                                                                                                                                   |
| **Lecturer**     | Allan Omondi                                                                                                                                                                                                                                                                              |
| **Contact**      | aomondi@strathmore.edu                                                                                                                                                                                                                                                                    |
| **Note**         | The lecture contains both theory and practice.<br/>This notebook forms part of the practice.<br/>It is intended for educational purposes only.<br/>Recommended citation: [BibTex](https://raw.githubusercontent.com/course-files/ServingMLModels/refs/heads/main/RecommendedCitation.bib) |

## Technology Stack

<p align="left">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" width="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/jupyter/jupyter-original-wordmark.svg" width="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/git/git-original.svg" width="40"/>
</p>

## Repository Structure

```text
.
├── Docker-Compose.yaml
├── LICENSE
├── Procfile
├── README.md
├── RecommendedCitation.bib
├── api.py
├── app_server_reverse_proxy_server_setup.md
├── assets
│   └── images
│       └── https_localhost.png
├── container-volumes
│   └── nginx
│       ├── certs
│       │   ├── selfsigned.crt
│       │   └── selfsigned.key
│       └── nginx.conf
├── docker-compose-dev.yaml
├── docker-compose-prod.yaml
├── frontend
│   ├── Proxies.png
│   ├── RequestFlow.jpg
│   ├── RequestFlow.png
│   ├── api_consumer.py
│   ├── api_test_DT_classifier.html
│   ├── api_test_DT_regressor.html
│   └── index.html
├── huggingface-spaces-using-gradio
│   ├── app.py
│   └── requirements.txt
├── images
│   ├── Dockerfile.flask-gunicorn-app
│   └── Dockerfile.nginx
├── lab_submission_instructions.md
├── model
│   ├── decisiontree_classifier_baseline.pkl
│   ├── decisiontree_regressor_optimum.pkl
│   ├── knn_classifier_optimum.pkl
│   ├── label_encoders_1b.pkl
│   ├── label_encoders_2.pkl
│   ├── label_encoders_4.pkl
│   ├── label_encoders_5.pkl
│   ├── naive_Bayes_classifier_optimum.pkl
│   ├── onehot_encoder_3.pkl
│   ├── random_forest_classifier_optimum.pkl
│   ├── scaler_4.pkl
│   ├── scaler_5.pkl
│   └── support_vector_classifier_optimum.pkl
├── publicly_serving_the_model_for_validation_by_domain_experts.md
├── requirements.txt
├── rules
├── runtime.txt
├── setup_instructions.md
└── streamlit-sharing-using-streamlit
    ├── app.py
    └── requirements.txt

12 directories, 44 files
```

## Setup Instructions

- [Setup Instructions](setup_instructions.md)

## Lab Manual

Refer to the files below for more details:

1. [api_consumer.py](frontend/api_consumer.py)
2. [api.py](api.py)
3. [api_test_DT_classifier.html](frontend/api_test_DT_classifier.html)
4. [api_test_DT_regressor.html](frontend/api_test_DT_regressor.html)
5. [Reverse Proxy Server and Application Server Setup](app_server_reverse_proxy_server_setup.md)
6. [Publicly Serving the Model for Validation by Domain Experts](publicly_serving_the_model_for_validation_by_domain_experts.md)

## Lab Submission Instructions

- [Lab Submission Instructions](lab_submission_instructions.md)
