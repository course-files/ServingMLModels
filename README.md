# Serving Machine Learning Models through REST APIs using Flask in Python

| Key              | Value                                                                                                                                                                                                                                                                                     |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Course Codes** | BBT 4206                                                                                                                                                                                                                                                                                  |
| **Course Names** | BBT 4206: Business Intelligence II (Week 4-6 of 13)                                                                                                                                                                                                                                       |
| **Semester**     | August to November 2025                                                                                                                                                                                                                                                                   |
| **Lecturer**     | Allan Omondi                                                                                                                                                                                                                                                                              |
| **Contact**      | aomondi@strathmore.edu                                                                                                                                                                                                                                                                    |
| **Note**         | The lecture contains both theory and practice.<br/>This notebook forms part of the practice.<br/>It is intended for educational purposes only.<br/>Recommended citation: [BibTex](https://raw.githubusercontent.com/course-files/ServingMLModels/refs/heads/main/RecommendedCitation.bib) |

## Repository Structure

```text
.
├── LICENSE
├── README.md
├── api.py
├── frontend_tests
│   ├── api_consumer.py
│   ├── api_test_DT_classifier.html
│   └── api_test_DT_regressor.html
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
├── requirements.txt
├── rules
└── setup_instructions.md

4 directories, 22 files
```

## Setup Instructions

- [Setup Instructions](setup_instructions.md)

## Lab Manual

Refer to the files below for more details:

1. [api_consumer.py](frontend_tests/api_consumer.py)
2. [api.py](api.py)
3. [api_test_DT_classifier.html](frontend_tests/api_test_DT_classifier.html)
4. [api_test_DT_regressor.html](frontend_tests/api_test_DT_regressor.html)

## Lab Submission Instructions

- [Lab Submission Instructions](lab_submission_instructions.md)
