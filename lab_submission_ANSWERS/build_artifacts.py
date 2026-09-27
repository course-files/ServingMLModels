"""
build_artifacts.py

Regenerates the four datasets used across the course's labs and re-fits and
persists the four artifacts that api.py needs to load:

  1. model/sme_revenue_regression_pipeline.joblib          (Lab 1: Regression)
  2. model/sme_credit_risk_classification_pipeline.joblib  (Lab 2: Classification)
  3. model/mall_customer_segmentation.joblib                (Lab 6: Clustering)
  4. model/ecommerce_recommendation_rules.joblib            (Lab 7: Association Rule Mining)

This mirrors the exact fitting logic already executed and verified inside
lab1_regression.ipynb, lab2_classification.ipynb, 6_kmeans_clustering_v2.ipynb,
and 7_association_rule_mining_ecommerce.ipynb, so the artifacts it produces are
equivalent (same preprocessing, same final model family and hyperparameters)
to what those notebooks already saved -- it does not re-derive new choices.
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import joblib

RANDOM_STATE = 42
MODEL_DIR = "./model"
os.makedirs(MODEL_DIR, exist_ok=True)

sys.path.insert(0, "/mnt/user-data/outputs")


# ============================================================================
# 1. REGRESSION (Lab 1)
# ============================================================================
def build_regression_pipeline():
    print("=" * 70)
    print("1. Building regression pipeline (SME revenue)")
    print("=" * 70)

    from generate_sme_revenue_data import generate_dataset as generate_revenue_data
    df = generate_revenue_data()

    TARGET = "monthly_revenue_kes"
    feature_cols = [c for c in df.columns if c not in ["business_id", TARGET]]
    X = df[feature_cols].copy()
    y = df[TARGET].copy()

    from sklearn.model_selection import train_test_split
    revenue_bins = pd.qcut(df[TARGET], q=5, labels=False, duplicates="drop")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=revenue_bins
    )

    # Feature selection: drop the two highly-correlated redundant columns
    columns_to_drop_corr = ["advertising_budget_kes", "payroll_cost_kes"]
    X_train_fs = X_train.drop(columns=columns_to_drop_corr)
    X_test_fs = X_test.drop(columns=columns_to_drop_corr)

    y_train_log = np.log1p(y_train)
    y_test_log = np.log1p(y_test)

    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
    from sklearn.impute import SimpleImputer

    nominal_cols = ["sector", "county", "quarter"]
    ordinal_col = ["owner_education_level"]
    education_order = [["Primary", "Secondary", "Tertiary", "Postgraduate"]]

    foot_traffic_col = ["avg_daily_foot_traffic"]
    other_numeric_cols = [c for c in X_train_fs.select_dtypes(include=[np.number]).columns
                           if c not in foot_traffic_col]

    foot_traffic_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scaler", StandardScaler()),
    ])
    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    nominal_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    ordinal_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(categories=education_order)),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("foot_traffic", foot_traffic_pipeline, foot_traffic_col),
        ("numeric", numeric_pipeline, other_numeric_cols),
        ("nominal", nominal_pipeline, nominal_cols),
        ("ordinal", ordinal_pipeline, ordinal_col),
    ])

    # Notebook Stage 10 winner: tuned GradientBoostingRegressor. Re-run the same
    # small grid so the persisted pipeline matches the notebook's own best_params_.
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import GridSearchCV, KFold

    kfold = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    tuning_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", GradientBoostingRegressor(random_state=RANDOM_STATE)),
    ])
    param_grid = {
        "model__n_estimators": [100, 200, 300],
        "model__max_depth": [2, 3, 4],
        "model__learning_rate": [0.03, 0.1, 0.2],
    }
    grid_search = GridSearchCV(
        tuning_pipeline, param_grid, cv=kfold,
        scoring="neg_root_mean_squared_error", n_jobs=-1, verbose=0
    )
    grid_search.fit(X_train_fs, y_train_log)
    print(f"Best parameters: {grid_search.best_params_}")

    final_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", GradientBoostingRegressor(
            **{k.replace("model__", ""): v for k, v in grid_search.best_params_.items()},
            random_state=RANDOM_STATE)),
    ])
    final_pipeline.fit(X_train_fs, y_train_log)

    out_path = os.path.join(MODEL_DIR, "sme_revenue_regression_pipeline.joblib")
    joblib.dump(final_pipeline, out_path)
    print(f"Saved: {out_path}")

    # Sanity check: predict on a raw new-business row, exactly as api.py will do
    sample = pd.DataFrame([{
        "sector": "Technology", "county": "Nairobi", "quarter": "Q3",
        "business_age_years": 4.5, "num_employees": 12,
        "owner_education_level": "Tertiary", "monthly_marketing_spend_kes": 45000,
        "avg_daily_foot_traffic": np.nan, "online_presence_score": 78.0,
        "loan_amount_kes": 250000, "interest_rate_pct": 14.5,
        "inflation_rate_pct": 6.5, "competitor_density": 5,
        "customer_satisfaction_score": 4.2,
    }])
    pred = np.expm1(final_pipeline.predict(sample))[0]
    print(f"Sanity check -- predicted monthly revenue: {pred:,.0f} KES\n")
    return out_path


# ============================================================================
# 2. CLASSIFICATION (Lab 2)
# ============================================================================
def build_classification_pipeline():
    print("=" * 70)
    print("2. Building classification pipeline (SME credit risk)")
    print("=" * 70)

    from generate_sme_credit_risk_data import generate_dataset as generate_credit_data
    df = generate_credit_data()

    TARGET = "credit_risk_category"
    feature_cols = [c for c in df.columns if c not in ["applicant_id", TARGET]]
    X = df[feature_cols].copy()
    y = df[TARGET].copy()

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()

    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline as SkPipeline
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
    from sklearn.impute import SimpleImputer

    nominal_cols = ["sector", "county", "quarter", "loan_purpose"]
    ordinal_col = ["owner_education_level"]
    education_order = [["Primary", "Secondary", "Tertiary", "Postgraduate"]]

    collateral_col = ["collateral_value_kes"]
    other_numeric_cols = [c for c in numeric_cols if c not in collateral_col]

    collateral_pipeline = SkPipeline(steps=[
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scaler", StandardScaler()),
    ])
    numeric_pipeline = SkPipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    nominal_pipeline = SkPipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    ordinal_pipeline = SkPipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(categories=education_order)),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("collateral", collateral_pipeline, collateral_col),
        ("numeric", numeric_pipeline, other_numeric_cols),
        ("nominal", nominal_pipeline, nominal_cols),
        ("ordinal", ordinal_pipeline, ordinal_col),
    ])

    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.over_sampling import SMOTE, ADASYN
    from imblearn.under_sampling import RandomUnderSampler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GridSearchCV, StratifiedKFold

    stratified_kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    tuning_pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("resampler", SMOTE(random_state=RANDOM_STATE)),
        ("model", RandomForestClassifier(random_state=RANDOM_STATE)),
    ])
    param_grid = {
        "resampler": [SMOTE(random_state=RANDOM_STATE), ADASYN(random_state=RANDOM_STATE),
                      RandomUnderSampler(random_state=RANDOM_STATE)],
        "model__n_estimators": [200, 300],
        "model__max_depth": [6, 8, 12],
        "model__class_weight": [None, "balanced"],
    }
    grid_search = GridSearchCV(
        tuning_pipeline, param_grid, cv=stratified_kfold,
        scoring="f1_macro", n_jobs=-1, verbose=0
    )
    grid_search.fit(X_train, y_train)
    print(f"Best parameters: {grid_search.best_params_}")

    best_params_clean = {k.replace("model__", ""): v for k, v in grid_search.best_params_.items()
                          if k.startswith("model__")}
    final_pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("resampler", grid_search.best_params_["resampler"]),
        ("model", RandomForestClassifier(**best_params_clean, random_state=RANDOM_STATE)),
    ])
    final_pipeline.fit(X_train, y_train)

    out_path = os.path.join(MODEL_DIR, "sme_credit_risk_classification_pipeline.joblib")
    joblib.dump(final_pipeline, out_path)
    print(f"Saved: {out_path}")

    sample = X_test.iloc[[0]]
    pred = final_pipeline.predict(sample)[0]
    print(f"Sanity check -- predicted credit risk category for a test applicant: {pred}\n")
    return out_path


# ============================================================================
# 3. CLUSTERING (Lab 6)
# ============================================================================
def build_clustering_pipeline():
    print("=" * 70)
    print("3. Building clustering artifact (mall customer segmentation)")
    print("=" * 70)

    customer_data = pd.read_csv("/home/claude/data/mall_customers.csv")

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    numeric_cols = ["Age", "Annual Income (k$)", "Spending Score (1-100)"]
    X = customer_data[numeric_cols].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Notebook's chosen k (k=5; see the elbow-vs-metrics discussion in the notebook)
    k = 5
    kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    kmeans.fit(X_scaled)

    out_path = os.path.join(MODEL_DIR, "mall_customer_segmentation.joblib")
    joblib.dump({"scaler": scaler, "kmeans": kmeans}, out_path)
    print(f"Saved: {out_path}")

    sample = pd.DataFrame([{"Age": 27, "Annual Income (k$)": 45, "Spending Score (1-100)": 72}])
    cluster = kmeans.predict(scaler.transform(sample))[0]
    print(f"Sanity check -- sample customer assigned to cluster: {cluster}\n")
    return out_path


# ============================================================================
# 4. ASSOCIATION RULE MINING (Lab 7)
# ============================================================================
def build_arm_artifact():
    print("=" * 70)
    print("4. Building association-rule-mining artifact (e-commerce recommender)")
    print("=" * 70)

    from generate_ecommerce_orders import generate_orders
    orders = generate_orders()
    orders["order_date"] = pd.to_datetime(orders["order_date"])

    transactions = orders.groupby("order_id")["sku"].apply(list).tolist()
    sku_lookup = orders.drop_duplicates("sku").set_index("sku")[
        ["product_name", "category", "unit_price_kes"]
    ]

    from mlxtend.preprocessing import TransactionEncoder
    from mlxtend.frequent_patterns import apriori, association_rules

    encoder = TransactionEncoder()
    onehot = encoder.fit(transactions).transform(transactions)
    transaction_data = pd.DataFrame(onehot, columns=encoder.columns_)

    MIN_SUPPORT = 0.01
    frequent_itemsets = apriori(transaction_data, min_support=MIN_SUPPORT, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

    CONFIDENCE_THRESHOLD = 0.5
    LIFT_THRESHOLD = 3.0
    strong_rules = rules[
        (rules["confidence"] >= CONFIDENCE_THRESHOLD) & (rules["lift"] >= LIFT_THRESHOLD)
    ].sort_values(["lift", "confidence"], ascending=[False, False])

    def remove_subset_redundant_rules(rules_df):
        rules_df = rules_df.sort_values(["lift", "confidence"], ascending=[False, False]).reset_index(drop=True)
        kept_rules = []
        for _, row in rules_df.iterrows():
            is_redundant = False
            for kept in kept_rules:
                if (row["consequents"] == kept["consequents"]
                        and row["antecedents"].issuperset(kept["antecedents"])
                        and row["antecedents"] != kept["antecedents"]):
                    is_redundant = True
                    break
            if not is_redundant:
                kept_rules.append(row)
        return pd.DataFrame(kept_rules)

    def remove_bidirectional_redundancy(rules_df):
        seen_pairs = set()
        kept_rows = []
        for _, row in rules_df.iterrows():
            pair_key = frozenset([frozenset(row["antecedents"]), frozenset(row["consequents"])])
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                kept_rows.append(row)
        return pd.DataFrame(kept_rows)

    nonredundant_rules = remove_subset_redundant_rules(strong_rules)
    cleaned_rules = remove_bidirectional_redundancy(nonredundant_rules)
    cleaned_rules = cleaned_rules.sort_values(["lift", "confidence"], ascending=[False, False]).reset_index(drop=True)
    print(f"Strong rules: {len(strong_rules)} -> cleaned rules: {len(cleaned_rules)}")

    def build_recommendation_lookup(rules_df):
        lookup = {}
        for _, row in rules_df.iterrows():
            key = frozenset(row["antecedents"])
            for consequent_sku in row["consequents"]:
                lookup.setdefault(key, []).append((consequent_sku, row["confidence"], row["lift"]))
        for key in lookup:
            lookup[key] = sorted(lookup[key], key=lambda x: x[1], reverse=True)
        return lookup

    recommendation_lookup = build_recommendation_lookup(cleaned_rules)

    out_path = os.path.join(MODEL_DIR, "ecommerce_recommendation_rules.joblib")
    joblib.dump({
        "cleaned_rules": cleaned_rules,
        "recommendation_lookup": recommendation_lookup,
        "sku_lookup": sku_lookup,
    }, out_path)
    print(f"Saved: {out_path}")

    def recommend(cart, lookup, sku_lookup_table, top_n=3):
        cart = set(cart)
        candidates = {}
        for antecedent, consequent_list in lookup.items():
            if antecedent.issubset(cart):
                for sku, confidence, lift in consequent_list:
                    if sku not in cart:
                        if sku not in candidates or confidence > candidates[sku][0]:
                            candidates[sku] = (confidence, lift)
        ranked = sorted(candidates.items(), key=lambda x: x[1][0], reverse=True)[:top_n]
        return [{"sku": sku, "product_name": sku_lookup_table.loc[sku, "product_name"],
                  "confidence": round(conf, 3), "lift": round(lift, 2)}
                for sku, (conf, lift) in ranked]

    example_cart = set(list(sku_lookup.index)[:2])
    recs = recommend(example_cart, recommendation_lookup, sku_lookup, top_n=3)
    print(f"Sanity check -- recommendations for cart {example_cart}: {recs}\n")
    return out_path


if __name__ == "__main__":
    t0 = time.time()
    build_regression_pipeline()
    build_classification_pipeline()
    build_clustering_pipeline()
    build_arm_artifact()
    print("=" * 70)
    print(f"All four artifacts built in {time.time() - t0:.1f}s")
    print("=" * 70)
    for f in sorted(os.listdir(MODEL_DIR)):
        size_kb = os.path.getsize(os.path.join(MODEL_DIR, f)) / 1024
        print(f"  {f}  ({size_kb:.1f} KB)")
