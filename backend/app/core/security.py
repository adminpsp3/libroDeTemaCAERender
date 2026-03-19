from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # Truncate to 72 to be 100% safe with bcrypt limits
    safe_password = str(plain_password)[:72]
    # Debug print to help identify what's being sent
    print(f"DEBUG: Verifying password of length {len(plain_password)}. Truncated to {len(safe_password)}")
    try:
        return pwd_context.verify(safe_password, hashed_password)
    except Exception as e:
        if "72 bytes" in str(e):
            # Fallback for older passlib/bcrypt versions
            import bcrypt
            return bcrypt.checkpw(safe_password.encode('utf-8'), hashed_password.encode('utf-8'))
        raise e

def get_password_hash(password):
    safe_password = str(password)[:72]
    return pwd_context.hash(safe_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
