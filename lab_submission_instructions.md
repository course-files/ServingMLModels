# Lab Submission Instructions: BBT 4206 - CAT 1 (Takeaway) - Due Date: 30th September 2025

## Student Details

**Name of the team on GitHub Classroom:**

**Team Member Contributions**

**Member 1**

| **Details**                                                                                        | **Comment** |
|:---------------------------------------------------------------------------------------------------|:------------|
| **Student ID**                                                                                     |             |
| **Name**                                                                                           |             |
| **What part of the lab did you personally contribute to,** <br>**and what did you learn from it?** |             |

**Member 2**

| **Details**                                                                                        | **Comment** |
|:---------------------------------------------------------------------------------------------------|:------------|
| **Student ID**                                                                                     |             |
| **Name**                                                                                           |             |
| **What part of the lab did you personally contribute to,** <br>**and what did you learn from it?** |             |

**Member 3**

| **Details**                                                                                        | **Comment** |
|:---------------------------------------------------------------------------------------------------|:------------|
| **Student ID**                                                                                     |             |
| **Name**                                                                                           |             |
| **What part of the lab did you personally contribute to,** <br>**and what did you learn from it?** |             |

**Member 4**

| **Details**                                                                                        | **Comment** |
|:---------------------------------------------------------------------------------------------------|:------------|
| **Student ID**                                                                                     |             |
| **Name**                                                                                           |             |
| **What part of the lab did you personally contribute to,** <br>**and what did you learn from it?** |             |

**Member 5**

| **Details**                                                                                        | **Comment** |
|:---------------------------------------------------------------------------------------------------|:------------|
| **Student ID**                                                                                     |             |
| **Name**                                                                                           |             |
| **What part of the lab did you personally contribute to,** <br>**and what did you learn from it?** |             |

## Scenario

You have trained various models for regression and classification problems.
You have also used k-Means clustering to identify clusters of clients.
Lastly, you have created association rules to identify products that are frequently bought together.

You are now required to create an API that serves the models and gives recommendations based on the association rules.
This API can be used by systems developed by other teams in the organization using different programming languages.

### Part A

- Refer to the lab on Regression and Classification available [here](https://github.com/course-files/RegressionAndClassification) to understand how the following models were trained:
  - Decision tree regressor
  - Decision tree classifier
  - Naive Bayes classifier
  - K-Nearest Neighbors (kNN) classifier
  - Support Vector Machine (SVM) classifier
  - Random Forest classifier
- Update [api.py](api.py) to include end-points to serve the following models loaded from disk:
  - Naive Bayes classifier
  - K-Nearest Neighbors (kNN) classifier
  - Support Vector Machine (SVM) classifier
  - Random Forest classifier

### Part B

- Refer to the lab on Clustering and Association Rule Mining available [here](https://github.com/course-files/ClusteringandAssociationRuleMining) to understand how the following clusters and association rules were created:
  - k-Means clustering
  - Apriori algorithm for association rule mining based on the "groceries" dataset by Hahsler et al. (2011) that contains 9,835 market basket transactions
- Update [api.py](api.py) to include end-points to serve the following:
  - A recommender that recommends products to a client based on the association rules created in the previous lab. The association rules should be loaded from disk.
  - A classifier that predicts the cluster to which a client belongs to. The classifier should be loaded from disk.

**Note 1:** **`api.py` is NOT production-grade as it is.** It is only meant for demonstration purposes. 
Scalability and security must be taken into consideration before deploying an API in a production environment.

**Note 2:** Students often treat the API as an afterthought, focusing only on training ML models.
In practice, the API is the product — it is how others interact with your model.
The "hidden" learning here is that the delivery mechanism (API design, usability, error handling, and even documentation) often matters more to stakeholders in the industry than the models themselves.

**Baseline (Required):**

- Update [api.py](api.py) to include end-points to serve at least three of the models trained in the previous lab

**Intermediate (Recommended):**

- Update [api.py](api.py) to include end-points to serve the following models:
  - Naive Bayes classifier
  - K-Nearest Neighbors (kNN) classifier
  - Support Vector Machine (SVM) classifier
  - Random Forest classifier

- Update [api.py](api.py) to include end-points to serve the following:
  - A recommender that recommends products to a client based on the association rules created in the previous lab

**Advanced (Optional):**

- Update [api.py](api.py) to include end-points to serve the following:
  - A classifier that predicts the cluster to which a client belongs to
- Create a web page (HTML and JavaScript) that demonstrates the use of the API
- Implement basic error handling (e.g., missing inputs).
- Flask comes with a development server (good for testing in development, bust unsafe for production).
In production, you need a server that can handle many users, concurrency, and failures. That is where **Gunicorn** comes in. It is a Web Server Gateway Interface (WSGI) server built for production.
- Instead of installing Flask + Gunicorn manually on your machine, you put everything into a Docker image. That image is like a sealed box: it contains your Python code, dependencies, and Gunicorn.
When you run the container, it behaves like a lightweight server.
- How the pieces should fit together:
  - Create a Dockerfile to tell Docker how to build the image (Python, install dependencies, run Gunicorn).
  - Build the Docker image: A one-time process to create a reusable package.
  - Run the container: Starts Gunicorn, serving your Flask app (runs the Flask app and handles requests).

- Dockerize (wrap everything into a container that can run anywhere) your Flask API using Gunicorn to make it "production-ready". Make use of a reverse-proxy (Nginx) to shield Gunicorn from the Internet.

- Why this is production-friendly
  - Portability: the same image runs anywhere (laptop, server, cloud).
  - Consistency: no “but it works on my machine” problems.
  - Isolation: your app runs in its own environment, safe from system changes.
  - Scalability: you can run more containers if you need more capacity.

### Video Demonstration

For all the three levels, submit the link to a short video (not more than 8 minutes) demonstrating the use of the API.

| **Key**                | **Value** |
|:-----------------------|:----------|
| **Link to the video:** |           |

### Grading Approach

- Baseline = Pass >= 60%
- Intermediate = Merit 75–85%
- Advanced = Distinction >= 86%
