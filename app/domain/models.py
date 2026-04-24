from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
import datetime

class Decision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REVIEW = "REVIEW"

class CreditApplication(BaseModel):
    age: int
    monthly_income: float
    employment_years: float
    loan_amount: float
    loan_term_months: int
    interest_rate: float
    past_due_30d: int
    inquiries_6m: int

class FeatureImportance(BaseModel):
    feature: str
    impact: float
    description: str # e.g., "Увеличивает риск на 5.2%"

class ScoringResult(BaseModel):
    probability: float
    base_value: float
    decision: Decision
    explanation: List[FeatureImportance]
    message: str
    analysis_summary: str
    is_verified: bool = False

# --- Auth & User Models ---

class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    passport_id: Optional[str] = None
    pin: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Bureau Report Models ---

class BureauRequest(BaseModel):
    user_id: str
    consent_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    passport_id: Optional[str] = None
    personal_number: Optional[str] = None
    request_source: str = "WEB"

# --- Consent Models ---

class ConsentCreate(BaseModel):
    credit_bureau_access: bool

class ConsentResponse(BaseModel):
    id: int
    user_id: int
    consent_type: str
    status: str
    timestamp: datetime.datetime

class BureauReportResponse(BaseModel):
    success: bool
    bureau_reference: str
    credit_score: int
    risk_level: str
    active_loans: int
    total_outstanding: float
    delinquencies_30d: int
    delinquencies_90d: int
    hard_inquiries_6m: int
    fetched_at: str
