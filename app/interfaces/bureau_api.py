from fastapi import APIRouter, Depends, HTTPException, status, Header

# Security: API Key for Bureau integration
BUREAU_API_KEY = "bank_secret_2026"

async def verify_bureau_key(x_api_key: str = Header(...)):
    if x_api_key != BUREAU_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Bureau API Key")

router = APIRouter(dependencies=[Depends(verify_bureau_key)])
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import datetime
from app.infrastructure.database import AsyncSessionLocal, UserDB, BureauReportDB
from app.domain.models import BureauRequest, BureauReportResponse
from app.infrastructure.bureau_service import BureauService
from app.interfaces.user_api import get_current_user, get_db

router = APIRouter()

from app.infrastructure.security import decrypt_data
from app.infrastructure.database import UserConsentDB
from app.domain.models import ConsentCreate, ConsentResponse

@router.post("/consent", response_model=ConsentResponse)
async def give_consent(
    consent: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # Check if consent already exists
    existing_query = await db.execute(
        select(UserConsentDB)
        .filter(UserConsentDB.user_id == current_user.id, UserConsentDB.consent_type == "credit_bureau_access")
    )
    existing = existing_query.scalars().first()
    
    if existing:
        existing.status = "granted" if consent.credit_bureau_access else "revoked"
        existing.timestamp = datetime.datetime.utcnow()
        db_consent = existing
    else:
        db_consent = UserConsentDB(
            user_id=current_user.id,
            consent_type="credit_bureau_access",
            status="granted" if consent.credit_bureau_access else "revoked"
        )
        db.add(db_consent)
    
    await db.commit()
    await db.refresh(db_consent)
    return db_consent

@router.post("/credit-report", response_model=BureauReportResponse)
async def get_bureau_report(
    request: BureauRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # 1. Проверка Consent
    consent_query = await db.execute(
        select(UserConsentDB)
        .filter(UserConsentDB.user_id == current_user.id, UserConsentDB.consent_type == "credit_bureau_access")
    )
    consent = consent_query.scalars().first()
    if not consent or consent.status != "granted":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Необходимо дать согласие на запрос данных в Бюро")

    # 2. Верификация данных (Decrypt stored data to compare)
    stored_passport = decrypt_data(current_user.encrypted_passport_id)
    stored_pin = decrypt_data(current_user.encrypted_pin)

    if request.passport_id and stored_passport:
        if request.passport_id != stored_passport:
            raise HTTPException(status_code=403, detail="Неверный ID паспорта")
    
    if request.personal_number and stored_pin:
        if request.personal_number != stored_pin:
            raise HTTPException(status_code=403, detail="Неверный ПИН-код карты")

    # 3. Подготовка данных для верификации в Бюро
    profile_data = {
        "first_name": request.first_name or current_user.first_name,
        "last_name": request.last_name or current_user.last_name,
        "document_number": request.passport_id,
        "personal_number": request.personal_number,
        "consent_reference": request.consent_id
    }

    # 4. Проверка на "свежесть" последнего отчета (младше 24 часов)
    # Мы пропускаем кэш, если переданы новые данные для верификации, 
    # чтобы всегда можно было протестировать разные профили
    if not request.passport_id:
        last_report_query = await db.execute(
            select(BureauReportDB)
            .filter(BureauReportDB.user_id == current_user.id)
            .order_by(BureauReportDB.created_at.desc())
        )
        last_report = last_report_query.scalars().first()
        
        if last_report and (datetime.datetime.utcnow() - last_report.created_at).total_seconds() < 86400:
            return BureauReportResponse(**json.loads(last_report.raw_response))
        # Если отчет свежий, возвращаем его из базы
        return BureauReportResponse(**json.loads(last_report.raw_response))

    try:
        # 5. Запрос во внешнее бюро
        report = await BureauService.get_full_credit_report(profile_data, request.consent_id)

        # 6. Сохранение в базу
        db_report = BureauReportDB(
            user_id=current_user.id,
            bureau_reference=report.bureau_reference,
            credit_score=report.credit_score,
            risk_level=report.risk_level,
            raw_response=report.json()
        )
        db.add(db_report)
        await db.commit()

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bureau integration error: {str(e)}")
