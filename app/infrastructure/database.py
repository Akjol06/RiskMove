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
        await conn.run_sync(Base.metadata.create_all)
    
    # Seeding test users from fixtures
    from app.infrastructure.fixtures.bureau_fixtures import BUREAU_FIXTURES
    from app.infrastructure.security import encrypt_data
    from app.application.auth_service import get_password_hash
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        for key, fix in BUREAU_FIXTURES.items():
            # Check if user exists
            username = f"user_{key.lower()}"
            result = await session.execute(select(UserDB).filter(UserDB.username == username))
            if not result.scalars().first():
                new_user = UserDB(
                    username=username,
                    email=f"{key.lower()}@example.com",
                    hashed_password=get_password_hash("password123"),
                    first_name=fix["first_name"],
                    last_name=fix["last_name"],
                    encrypted_passport_id=encrypt_data(fix["passport_id"]),
                    encrypted_pin=encrypt_data(fix["personal_number"]),
                    phone_number="+996700112233"
                )
                session.add(new_user)
        await session.commit()
