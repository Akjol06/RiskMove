import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from app.domain.models import CreditApplication, ScoringResult, Decision, FeatureImportance

class MLScoringModel:
    def __init__(self, model_path: Path, explainer_path: Path, features_path: Path):
        self.model = joblib.load(model_path)
        self.explainer = joblib.load(explainer_path)
        self.features = joblib.load(features_path)

    def predict(self, application: CreditApplication) -> ScoringResult:
        # Convert domain entity to DataFrame
        data = pd.DataFrame([application.dict()])
        data = data[self.features] # Ensure order
        
        # Get probability
        prob = float(self.model.predict_proba(data)[0, 1])
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(data)
        
        # Handle SHAP output format for RandomForest (list of arrays or 3D array)
        if isinstance(shap_values, list):
            # Typically shap_values[1] for binary classification class 1
            impacts = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(shap_values.shape) == 3:
            # If 3D, usually (samples, features, classes)
            impacts = shap_values[0, :, 1]
        else:
            # If 2D, (samples, features)
            impacts = shap_values[0]
            
        explanation = [
            FeatureImportance(feature=f, impact=float(i))
            for f, i in zip(self.features, impacts)
        ]
        
        # Sort by absolute impact
        explanation.sort(key=lambda x: abs(x.impact), reverse=True)
        
        # Decision logic
        if prob < 0.3:
            decision = Decision.APPROVE
            message = "Заявка одобрена на основе низкого профиля риска."
        elif prob < 0.7:
            decision = Decision.REVIEW
            message = "Заявка требует ручной проверки из-за умеренного риска."
        else:
            decision = Decision.REJECT
            message = "Заявка отклонена из-за высокого профиля риска."
            
        return ScoringResult(
            probability=prob,
            decision=decision,
            explanation=explanation[:5], # Return top 5 influential features
            message=message
        )
