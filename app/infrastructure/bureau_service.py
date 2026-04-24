import random
import datetime
import json
from app.infrastructure.fixtures.bureau_fixtures import BUREAU_FIXTURES
from app.domain.models import BureauReportResponse

class BureauService:
    @staticmethod
    def fetch_credit_history(passport_id: str, pin: str):
        """
        Legacy mock method for simple scoring.
        """
        return {
            "credit_score": random.randint(300, 850),
            "total_loans": random.randint(0, 10),
            "current_delinquencies": random.randint(0, 2),
            "bureau_confirmed": True
        }

    @staticmethod
    async def get_full_credit_report(profile_data: dict, consent_id: str) -> BureauReportResponse:
        """
        Mocked service to fetch full credit report with identity validation.
        Matches against BUREAU_FIXTURES based on passport_id, personal_number, first_name, last_name.
        """
        first_name = profile_data.get("first_name")
        last_name = profile_data.get("last_name")
        passport_id = profile_data.get("document_number")
        personal_number = profile_data.get("personal_number")

        matched_data = None
        
        # Try to find a match in fixtures
        for key, fixture in BUREAU_FIXTURES.items():
            if (fixture["passport_id"] == passport_id and 
                fixture["personal_number"] == personal_number and
                fixture["first_name"].lower() == first_name.lower() and
                fixture["last_name"].lower() == last_name.lower()):
                matched_data = fixture
                break
        
        if not matched_data:
            # If no match found, we simulate "No History Found" or return an error
            # For the hackaton, we can return a random "New User" report or raise error
            # The user asked to "look in base if they exist", implying error if not.
            raise ValueError("Данные не найдены в базе Кредитного Бюро. Проверьте правильность ввода.")

        report = BureauReportResponse(
            success=True,
            bureau_reference=f"CB-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(100000, 999999)}",
            credit_score=matched_data["credit_score"],
            risk_level=matched_data["risk_level"],
            active_loans=matched_data["active_loans"],
            total_outstanding=matched_data["total_outstanding"],
            delinquencies_30d=matched_data["delinquencies_30d"],
            delinquencies_90d=0,
            hard_inquiries_6m=matched_data["hard_inquiries_6m"],
            fetched_at=datetime.datetime.utcnow().isoformat() + "Z"
        )
        return report

    @staticmethod
    def verify_consent(user_id: int):
        return True
