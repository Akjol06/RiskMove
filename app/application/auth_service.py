from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import UserDB
from app.domain.models import UserCreate
import os
from dotenv import load_dotenv

load_dotenv()

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from app.infrastructure.security import encrypt_data

class AuthService:
    @staticmethod
    async def get_user(db: AsyncSession, username: str):
        result = await db.execute(select(UserDB).filter(UserDB.username == username))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(UserDB).filter(UserDB.email == email))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = UserDB(
            username=user.username, 
            email=user.email, 
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            encrypted_passport_id=encrypt_data(user.passport_id),
            encrypted_pin=encrypt_data(user.pin)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        user = await AuthService.get_user(db, username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
