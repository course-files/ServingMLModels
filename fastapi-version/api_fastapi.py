"""
api_fastapi.py

This is the FastAPI version of api.py. It is an optional alternative, not a
replacement: you may build the lab using Flask (api.py, in the repository
root) or FastAPI (this file). Both serve the exact same four machine
learning artifacts, produced in earlier labs:

    1. Regression       -- SME monthly revenue prediction
    2. Classification   -- SME credit risk category
    3. Clustering       -- Mall customer segment assignment
    4. Association Rule -- Product recommendation from a cart
       Mining (ARM)

Both versions expose the same four URL paths, accept the same JSON request
bodies, and return the same JSON response bodies. This matters because the
frontend HTML pages, the api_consumer scripts, the Nginx reverse proxy
configuration, and the lab marking guide were all written against that
contract, not against Flask specifically. Whichever framework you choose,
the rest of the lab (Docker, Nginx, Render, Hugging Face, Streamlit) works
the same way, because none of those pieces call into Flask or FastAPI
directly; they only ever talk to the API over HTTP.

Read api.py first if you have not already. The comments below focus on
what changes when the same API is rebuilt with FastAPI, rather than
re-explaining the machine learning pipeline logic, which is identical in
both files.

Run this file directly to start a local development server:

    python api_fastapi.py

or, equivalently, using the uvicorn command line tool directly:

    uvicorn api_fastapi:app --reload --port 5000

Once it is running, open this in your browser:

    http://127.0.0.1:5000/docs

FastAPI builds that interactive documentation page automatically from the
Pydantic models and type hints below. You can expand each endpoint, fill in
an example request body, and send a real request to your own running
server directly from the browser, with no Postman or curl needed. This is
one of the main practical differences from Flask, which does not generate
this page on its own.
"""

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(
    title="ServingMLModels API (FastAPI version)",
    description=(
        "Serves four machine learning artifacts: an SME revenue regressor, "
        "an SME credit risk classifier, a mall customer segmenter, and an "
        "e-commerce product recommender."
    ),
    version="1.0.0",
)

# -----------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
# -----------------------------------------------------------------------
# Flask uses the flask_cors package and a CORS(app, resources={...}) call.
# FastAPI (built on Starlette) ships its own CORSMiddleware, added with
# app.add_middleware(...) instead. The list of trusted origins below is the
# same list used in api.py, including the literal string "null", which is
# the Origin header a browser sends when a frontend .html file is opened
# directly from disk (file://) rather than served from a web server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000", "http://127.0.0.1:5000",
        "http://localhost:5500", "http://127.0.0.1:5500",
        "https://localhost:443", "https://127.0.0.1:443",
        "http://localhost:63342",  # VS Code Live Server extension
        "null",  # allows opening a frontend .html file directly (file://) with no web server
    ],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------
# Load the four persisted artifacts ONCE, at startup, exactly as api.py
# does. This part of the lesson does not change between Flask and FastAPI:
# the fitted model never changes while the server is running, so loading it
# inside a route function on every request would be slow and pointless.
#
# One small but important difference from api.py's MODEL_DIR = "./model":
# api.py lives at the repository root, right next to the model/ folder, so
# a path relative to the current working directory works as long as you
# launch it from the repository root. This file lives one level down, in
# fastapi-version/, and it can be started in more than one way (running
# "python fastapi-version/api_fastapi.py" from the repository root, or
# running "uvicorn api_fastapi:app" from inside this folder), each of
# which leaves Python's current working directory pointed somewhere
# different. Building the path from this file's own location, with
# pathlib, instead of from the current working directory, means the model
# files are found correctly no matter which of those two ways you start
# the server. This is the same kind of path bug that affects a Streamlit
# Community Cloud deployment when model/ is not where the app expects it;
# resolving the path from the file itself avoids it entirely.
#
# The model/ folder is in a different place depending on where this file is
# running, so two locations are checked, in order:
#   1. Next to this file. This is the layout inside the Docker container,
#      where the Dockerfile copies api_fastapi.py and model/ into the same
#      folder (/opt/app-smm-fastapi/).
#   2. One folder above this file. This is the layout in the repository,
#      where this file is in fastapi-version/ and model/ is at the
#      repository root.
_HERE = Path(__file__).resolve().parent
MODEL_DIR = _HERE / "model" if (_HERE / "model").is_dir() else _HERE.parent / "model"

regression_pipeline = joblib.load(
    os.path.join(MODEL_DIR, "lasso_regressor_for_sme_revenue.joblib")
)

classification_pipeline = joblib.load(
    os.path.join(MODEL_DIR, "svc_classifier_for_sme_credit_risk.joblib")
)

clustering_artifact = joblib.load(
    os.path.join(MODEL_DIR, "kmeans_mall_customer_segmentation.joblib")
)
clustering_scaler = clustering_artifact["scaler"]
clustering_kmeans = clustering_artifact["kmeans"]

arm_artifact = joblib.load(
    os.path.join(MODEL_DIR, "apriori_recommendation_rules.joblib")
)
recommendation_lookup = arm_artifact["recommendation_lookup"]
sku_lookup = arm_artifact["sku_lookup"]

print("All four artifacts have been loaded. The API is ready.")


# =========================================================================
# REQUEST BODY MODELS (the main new concept in this file)
# =========================================================================
# Flask's request.get_json() hands you a plain Python dictionary and trusts
# you to read the right keys out of it. If a user sends a request with a
# missing field, a misspelled key, or a string where a number was expected,
# Flask will not notice. The pipeline itself would either silently produce
# a wrong prediction or raise a confusing error deep inside scikit-learn.
#
# FastAPI instead asks you to describe the expected request body as a
# Pydantic model: a Python class whose attributes name each field and
# whose type hints state the expected type. FastAPI then does three
# things automatically before your route function ever runs:
#   1. Parses the incoming JSON body into this model.
#   2. Validates every field (right name present, right type, nullable
#      fields allowed to be null).
#   3. If anything does not match, returns a 422 Unprocessable Entity
#      response with a precise explanation of which field was wrong,
#      instead of running the route function at all.
# This is the single biggest practical difference you will notice
# compared to the Flask version: a badly formed request fails immediately with a
# clear, structured error message, rather than reaching the model at all.
#
# A field written as "something: float | None = None" is optional and may
# be sent as JSON null (or left out of the request body entirely). This is
# used below for avg_daily_foot_traffic and collateral_value_kes, which
# api.py's own comments explain are deliberately null for certain rows
# (structural missingness, not a mistake).
# -----------------------------------------------------------------------


class RevenueRegressionRequest(BaseModel):
    sector: str
    county: str
    quarter: str
    business_age_years: float
    num_employees: int
    owner_education_level: str
    monthly_marketing_spend_kes: float
    avg_daily_foot_traffic: float | None = None
    online_presence_score: float
    loan_amount_kes: float
    interest_rate_pct: float
    inflation_rate_pct: float
    competitor_density: int
    customer_satisfaction_score: float


class CreditRiskClassificationRequest(BaseModel):
    sector: str
    county: str
    quarter: str
    loan_purpose: str
    owner_education_level: str
    business_age_years: float
    num_employees: int
    monthly_revenue_kes: float
    loan_amount_kes: float
    loan_term_months: int
    interest_rate_pct: float
    collateral_value_kes: float | None = None
    debt_to_income_ratio: float
    credit_score: int
    num_previous_loans: int
    missed_payments_count: int
    online_presence_score: float
    customer_satisfaction_score: float
    competitor_density: int


# The mall customer segmentation model was trained on a DataFrame whose
# column names are "Age", "Annual Income (k$)", and "Spending Score
# (1-100)". None of those three strings are valid Python attribute names
# (they contain spaces, and one contains parentheses and a dollar sign), so
# they cannot be used directly as the names of class attributes below.
#
# Pydantic's solution is a Field alias: the attribute keeps a normal,
# valid Python name (age, annual_income_k, spending_score), but is told to
# read that attribute's value from a differently spelled key in the
# incoming JSON, using Field(alias="..."). model_config's
# populate_by_name=True simply allows the model to also be built directly
# from the Python-friendly names, which is convenient for testing.
class CustomerSegmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    age: int = Field(alias="Age")
    annual_income_k: float = Field(alias="Annual Income (k$)")
    spending_score: float = Field(alias="Spending Score (1-100)")


class CartRecommendationRequest(BaseModel):
    cart: list[str]
    top_n: int = 3


# =========================================================================
# ROUTES
# =========================================================================
# Three further small differences from Flask show up in every route below:
#
#   1. The HTTP method and path are both given in one decorator,
#      @app.post("/path"), instead of Flask's
#      @app.route("/path", methods=["POST"]).
#
#   2. The route function takes the request model as a normal function
#      parameter (for example, payload: RevenueRegressionRequest) instead
#      of calling request.get_json() inside the function body. FastAPI
#      reads the request body, builds this object, and validates it before
#      your function starts running.
#
#   3. The route function returns a plain Python dict (or a Pydantic
#      model). FastAPI converts it to a JSON response automatically, so
#      there is no equivalent of Flask's jsonify() call to remember.
#
#   4. None of these functions is declared "async def". They are ordinary
#      "def" functions. This is deliberate, not an oversight: see the note
#      directly above predict_revenue() below for why.
# -----------------------------------------------------------------------


# 1. REGRESSION -- predict monthly revenue (KES) for an SME

# Sample request (cURL):
#   curl -X POST http://127.0.0.1:5000/api/v1/models/sme-revenue-regressor/predictions \
#        -H "Content-Type: application/json" \
#        -d '{"sector": "Technology", "county": "Nairobi", "quarter": "Q3",
#             "business_age_years": 4.5, "num_employees": 12,
#             "owner_education_level": "Secondary",
#             "monthly_marketing_spend_kes": 45000,
#             "avg_daily_foot_traffic": null,
#             "online_presence_score": 78.0, "loan_amount_kes": 250000,
#             "interest_rate_pct": 14.5, "inflation_rate_pct": 6.5,
#             "competitor_density": 5, "customer_satisfaction_score": 4.2}'
#
# IMPORTANT, read this carefully if you are new to FastAPI: a route
# function that performs a slow, CPU-bound, ordinary (synchronous) piece of
# work, such as pipeline.predict() here, should be written as a normal
# "def" function, NOT "async def". FastAPI (through Starlette) runs a plain
# "def" route in a worker thread pool automatically, so one slow request
# does not block any other request from being handled at the same time.
#
# If this function were instead declared "async def" without actually
# awaiting anything inside it, the call to regression_pipeline.predict()
# would run directly on FastAPI's single event loop and block it completely
# until the prediction finishes. Every other request, to this endpoint or
# any other, would have to wait in line behind it, because the whole point
# of the event loop is that only one piece of code runs on it at a time.
# This would quietly undo the exact benefit that running multiple Gunicorn
# workers (see the Dockerfile in this folder) is meant to provide. It
# is one of the most common mistakes developers make when they are new to
# FastAPI and assume "async" always means "faster."
@app.post("/api/v1/models/sme-revenue-regressor/predictions")
def predict_revenue(payload: RevenueRegressionRequest):
    # payload is already a validated RevenueRegressionRequest object at this
    # point. model_dump() turns it back into a plain dictionary, in the
    # same shape Flask's request.get_json() would have returned, so the
    # rest of this function is identical to api.py's predict_revenue().
    input_row = pd.DataFrame([payload.model_dump()])

    predicted_log_revenue = regression_pipeline.predict(input_row)[0]
    # The pipeline was trained on log1p(revenue) because revenue was
    # right-skewed; we invert that single transformation here to report the
    # prediction in KES.
    predicted_revenue_kes = float(np.expm1(predicted_log_revenue))

    return {
        "predicted_monthly_revenue_kes": round(predicted_revenue_kes, 2),
        "model": "Lasso Regressor",
    }


# 2. CLASSIFICATION -- predict SME credit risk category (Low/Medium/High)

# Sample request (cURL):
#   curl -X POST http://127.0.0.1:5000/api/v1/models/sme-credit-risk-classifier/predictions \
#        -H "Content-Type: application/json" \
#        -d '{"sector": "Retail", "county": "Nairobi", "quarter": "Q2",
#             "loan_purpose": "Working Capital", "owner_education_level": "Secondary",
#             "business_age_years": 2.1, "num_employees": 4,
#             "monthly_revenue_kes": 850000, "loan_amount_kes": 150000,
#             "loan_term_months": 12, "interest_rate_pct": 16.5,
#             "collateral_value_kes": null, "debt_to_income_ratio": 0.62,
#             "credit_score": 590, "num_previous_loans": 1,
#             "missed_payments_count": 3, "online_presence_score": 40.0,
#             "customer_satisfaction_score": 3.4, "competitor_density": 6}'
#
# Note: collateral_value_kes is allowed to be null here (see
# CreditRiskClassificationRequest above) because "Working Capital" loans
# are more often unsecured. This is structural missingness, not a mistake
# in the request, and the pipeline's own imputer already handles it
# internally, exactly as in api.py.
@app.post("/api/v1/models/sme-credit-risk-classifier/predictions")
def predict_credit_risk(payload: CreditRiskClassificationRequest):
    input_row = pd.DataFrame([payload.model_dump()])

    predicted_class = classification_pipeline.predict(input_row)[0]
    predicted_probabilities = classification_pipeline.predict_proba(input_row)[0]
    class_labels = classification_pipeline.named_steps["model"].classes_

    return {
        "predicted_credit_risk_category": str(predicted_class),
        "class_probabilities": {
            str(label): round(float(prob), 4)
            for label, prob in zip(class_labels, predicted_probabilities)
        },
        "model": "Support Vector Classifier (tuned, SMOTE-resampled at training only)",
    }


# 3. CLUSTERING -- assign a new mall customer to an existing segment

# Sample request (cURL):
#   curl -X POST http://127.0.0.1:5000/api/v1/models/mall-customer-segmenter/predictions \
#        -H "Content-Type: application/json" \
#        -d '{"Age": 27, "Annual Income (k$)": 45, "Spending Score (1-100)": 72}'
#
# Note the request body still uses the original column names, exactly as
# in api.py; users sending requests to this endpoint see no difference
# at all. The alias mapping defined on CustomerSegmentRequest above is what
# makes this possible.
#
# by_alias=True on model_dump() is the other half of that same mapping: it
# rebuilds the dictionary using the ORIGINAL column names ("Age", not
# "age"), because clustering_scaler was fitted on a DataFrame with those
# exact column names and will raise an error if the columns do not match.
@app.post("/api/v1/models/mall-customer-segmenter/predictions")
def predict_customer_segment(payload: CustomerSegmentRequest):
    input_row = pd.DataFrame([payload.model_dump(by_alias=True)])

    scaled_input = clustering_scaler.transform(input_row)
    assigned_cluster = int(clustering_kmeans.predict(scaled_input)[0])

    return {
        "assigned_cluster": assigned_cluster,
        "model": "K-Means (k=5, standardized features)",
    }


# 4. ASSOCIATION RULE MINING -- recommend products for a shopping cart

# Sample request (cURL):
#   curl -X POST http://127.0.0.1:5000/api/v1/models/ecommerce-recommender/predictions \
#        -H "Content-Type: application/json" \
#        -d '{"cart": ["H06", "H07"]}'
#
#   curl -X POST http://127.0.0.1:5000/api/v1/models/ecommerce-recommender/predictions \
#        -H "Content-Type: application/json" \
#        -d '{"cart": ["P04", "P01"]}'
#
# Note: top_n defaults to 3 in CartRecommendationRequest above, so a
# request that leaves top_n out entirely is valid and behaves the same way
# api.py's payload.get("top_n", 3) did.
@app.post("/api/v1/models/ecommerce-recommender/predictions")
def recommend_products(payload: CartRecommendationRequest):
    cart = set(payload.cart)
    top_n = payload.top_n

    candidates = {}
    for antecedent, consequent_list in recommendation_lookup.items():
        if antecedent.issubset(cart):
            for sku, confidence, lift in consequent_list:
                if sku not in cart:
                    if sku not in candidates or confidence > candidates[sku][0]:
                        candidates[sku] = (confidence, lift)

    ranked = sorted(candidates.items(), key=lambda item: item[1][0], reverse=True)[:top_n]
    recommendations = [
        {
            "sku": str(sku),
            "product_name": sku_lookup.loc[sku, "product_name"],
            "confidence": round(float(confidence), 3),
            "lift": round(float(lift), 2),
        }
        for sku, (confidence, lift) in ranked
    ]

    return {
        "cart": sorted(cart),
        "recommendations": recommendations,
        "model": "Apriori association rules, cleaned + precomputed lookup",
    }


# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------
# Flask's app.run(debug=True, port=5000) starts a development server with
# an interactive, in-browser debugger. That debugger is convenient, but it
# is also a known security risk if it is ever left reachable outside your
# own machine: it can give anyone who can reach the server a console that
# executes arbitrary Python code.
#
# Uvicorn's development server, started with reload=True below, is
# different in one important way: reload=True only means the server
# restarts itself automatically when it notices a code change on disk. It
# does not add an interactive debugger console to error pages. There is no
# direct FastAPI equivalent of Flask's debug console, which removes that
# particular risk, but it also means error pages carry less detail by
# default. Either way, reload=True (like Flask's debug=True) is a
# development convenience only, and should never be left on when a server
# is reachable from outside your own machine.

# Every Python file has a built-in variable called __name__.
#   - When you run this file directly (python api_fastapi.py), Python sets
#     __name__ to "__main__", so the condition is True and the indented code runs.
#   - When another file or program imports this file (for example, Gunicorn
#     loading api_fastapi:app), __name__ is set to the file's name instead,
#     so the condition is False and the indented code is skipped.
# This lets the same file work in two ways: as a script you can start
# yourself, and as a module that other programs can import without
# accidentally starting a second development server.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_fastapi:app", host="127.0.0.1", port=5000, reload=True)

    # Production-style alternative (no auto-reload, listens on every
    # network interface so it can be reached from outside the container):
    # uvicorn.run("api_fastapi:app", host="0.0.0.0", port=5000, reload=False)