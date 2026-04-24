import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, confusion_matrix
import joblib
import shap
from pathlib import Path

def train():
    data_path = Path("data/credit_scoring_dataset.csv")
    df = pd.read_csv(data_path)
    
    feature_cols = [
        "age", "monthly_income", "employment_years", "loan_amount",
        "loan_term_months", "interest_rate", "past_due_30d", "inquiries_6m"
    ]
    
    X = df[feature_cols]
    y = df["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train RandomForest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)
    
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"ROC-AUC: {roc_auc:.4f}")
    print(f"PR-AUC: {pr_auc:.4f}")
    print(f"Accuracy: {acc:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save Model
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    joblib.dump(model, models_dir / "credit_model.joblib")
    
    # Save SHAP Explainer
    explainer = shap.TreeExplainer(model)
    joblib.dump(explainer, models_dir / "explainer.joblib")
    
    # Save features list for consistency
    joblib.dump(feature_cols, models_dir / "features.joblib")
    
    print("Model and Explainer saved to models/")

if __name__ == "__main__":
    train()
