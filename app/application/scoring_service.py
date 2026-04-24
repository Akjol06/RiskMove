from app.domain.models import CreditApplication, ScoringResult
from app.infrastructure.ml_model import MLScoringModel
from pathlib import Path

class ScoringService:
    def __init__(self):
        # Paths for the models
        base_path = Path(__file__).parent.parent.parent
        model_path = base_path / "models" / "credit_model.joblib"
        explainer_path = base_path / "models" / "explainer.joblib"
        features_path = base_path / "models" / "features.joblib"
        
        self.model = MLScoringModel(model_path, explainer_path, features_path)

    def execute(self, application: CreditApplication) -> ScoringResult:
        return self.model.predict(application)
