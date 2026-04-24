from app.domain.models import CreditApplication, ScoringResult
from app.infrastructure.ml_model import MLScoringModel
from pathlib import Path
from typing import Optional

class ScoringService:
    def __init__(self):
        # Paths for the models
        base_path = Path(__file__).parent.parent.parent
        model_path = base_path / "models" / "credit_model.joblib"
        explainer_path = base_path / "models" / "explainer.joblib"
        features_path = base_path / "models" / "features.joblib"
        
        self.model = MLScoringModel(model_path, explainer_path, features_path)

    def execute(self, application: CreditApplication, bureau_data: Optional[dict] = None) -> ScoringResult:
        """
        Executes scoring. If bureau_data is provided, it enriches/overrides application fields.
        """
        enriched_app = application
        
        if bureau_data:
            # Override with verified bureau data
            enriched_app.past_due_30d = bureau_data.get("delinquencies_30d", enriched_app.past_due_30d)
            enriched_app.inquiries_6m = bureau_data.get("hard_inquiries_6m", enriched_app.inquiries_6m)
            
            # We could also use bureau_data.get("credit_score") if the model supported it
            # For now, we trust bureau data more than user input for these specific fields
            
        result = self.model.predict(enriched_app)
        
        if bureau_data:
            result.message = f"[Verified by Bureau] {result.message}"
            result.analysis_summary = f"Данные подтверждены КБ. {result.analysis_summary}"
            result.is_verified = True
            
        return result
