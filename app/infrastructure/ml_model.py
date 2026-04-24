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
        
        # Get SHAP values and base value
        shap_values = self.explainer.shap_values(data)
        
        # Base value (expected value)
        if isinstance(self.explainer.expected_value, (list, np.ndarray)):
            base_val = float(self.explainer.expected_value[1])
        else:
            base_val = float(self.explainer.expected_value)

        # Handle SHAP output format for RandomForest
        if isinstance(shap_values, list):
            impacts = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(shap_values.shape) == 3:
            impacts = shap_values[0, :, 1]
        else:
            impacts = shap_values[0]
            
        feature_labels = {
            "age": "Возраст", "monthly_income": "Доход", "employment_years": "Стаж",
            "loan_amount": "Сумма кредита", "loan_term_months": "Срок",
            "interest_rate": "Ставка", "past_due_30d": "Просрочки", "inquiries_6m": "Запросы"
        }

        explanation = []
        summary_parts = []
        
        for f, i in zip(self.features, impacts):
            direction = "увеличивает" if i > 0 else "снижает"
            desc = f"{direction} риск на {abs(i)*100:.1f}%"
            explanation.append(FeatureImportance(
                feature=f, 
                impact=float(i),
                description=desc
            ))
            if abs(i) > 0.05: # Only include significant factors in summary
                summary_parts.append(f"{feature_labels.get(f, f)} {direction} вероятность дефолта на {abs(i)*100:.1f}%")

        # Sort by absolute impact
        explanation.sort(key=lambda x: abs(x.impact), reverse=True)
        
        analysis_summary = "Основные факторы: " + ", ".join(summary_parts) + "." if summary_parts else "Факторы влияния распределены равномерно."

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
            base_value=base_val,
            decision=decision,
            explanation=explanation[:5],
            message=message,
            analysis_summary=analysis_summary
        )
