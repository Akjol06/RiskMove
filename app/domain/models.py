from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

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

class ScoringResult(BaseModel):
    probability: float
    decision: Decision
    explanation: List[FeatureImportance]
    message: str
