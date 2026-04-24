from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import CreditApplication, ScoringResult
from app.application.scoring_service import ScoringService
from app.application.history_service import HistoryService
from app.interfaces.user_api import get_optional_current_user, get_current_user, get_db
from app.infrastructure.database import UserDB
from app.infrastructure.bureau_service import BureauService

router = APIRouter()
scoring_service = ScoringService()

from app.main import limiter
from fastapi import Request

@router.post("/predict", response_model=ScoringResult)
@limiter.limit("30/minute")
async def predict(
    request: Request,
    application: CreditApplication, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_current_user)
):
    try:
        bureau_info = None
        if current_user:
            # Check for fresh bureau report (last 24h)
            from sqlalchemy import select
            from app.infrastructure.database import BureauReportDB
            import json
            import datetime
            
            last_report_query = await db.execute(
                select(BureauReportDB)
                .filter(BureauReportDB.user_id == current_user.id)
                .order_by(BureauReportDB.created_at.desc())
            )
            last_report = last_report_query.scalars().first()
            
            if last_report and (datetime.datetime.utcnow() - last_report.created_at).total_seconds() < 86400:
                bureau_info = json.loads(last_report.raw_response)

        # Pass bureau_info if found
        result = scoring_service.execute(application, bureau_data=bureau_info)
        
        # If user is logged in, save to history
        if current_user:
            await HistoryService.save_result(db, current_user.id, result)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy"}
