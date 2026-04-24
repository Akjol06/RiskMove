from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import ScoringHistoryDB
from app.domain.models import ScoringResult

class HistoryService:
    @staticmethod
    async def save_result(db: AsyncSession, user_id: int, result: ScoringResult):
        db_history = ScoringHistoryDB(
            user_id=user_id,
            probability=result.probability,
            decision=result.decision.value,
            analysis_summary=result.analysis_summary
        )
        db.add(db_history)
        await db.commit()
        await db.refresh(db_history)
        return db_history

    @staticmethod
    async def get_user_history(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(ScoringHistoryDB)
            .filter(ScoringHistoryDB.user_id == user_id)
            .order_by(ScoringHistoryDB.created_at.desc())
        )
        return result.scalars().all()
