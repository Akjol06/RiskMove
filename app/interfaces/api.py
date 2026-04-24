from fastapi import APIRouter, HTTPException
from app.domain.models import CreditApplication, ScoringResult
from app.application.scoring_service import ScoringService

router = APIRouter()
scoring_service = ScoringService()

@router.post("/predict", response_model=ScoringResult)
async def predict(application: CreditApplication):
    try:
        result = scoring_service.execute(application)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy"}
