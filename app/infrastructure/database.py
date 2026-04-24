from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Profile fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    # Encrypted Sensitive Data
    encrypted_passport_id = Column(String, nullable=True)
    encrypted_pin = Column(String, nullable=True)
    
    histories = relationship("ScoringHistoryDB", back_populates="owner")
    bureau_reports = relationship("BureauReportDB", back_populates="owner")
    consents = relationship("UserConsentDB", back_populates="owner")

class UserConsentDB(Base):
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    consent_type = Column(String) # e.g., "credit_bureau_access"
    status = Column(String) # "granted", "revoked"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("UserDB", back_populates="consents")

class ScoringHistoryDB(Base):
    __tablename__ = "scoring_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    probability = Column(Float)
    decision = Column(String)
    analysis_summary = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("UserDB", back_populates="histories")

class BureauReportDB(Base):
    __tablename__ = "bureau_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bureau_reference = Column(String, unique=True)
    credit_score = Column(Integer)
    risk_level = Column(String)
    raw_response = Column(String) # Store JSON as string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("UserDB", back_populates="bureau_reports")

async def init_db():
    async with engine.begin() as conn:
        # For production, use Alembic migrations. For hackaton, create_all is fine.
        await conn.run_sync(Base.metadata.create_all)
