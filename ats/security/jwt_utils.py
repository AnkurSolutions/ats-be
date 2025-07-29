from jose import jwt, JWTError
from ats.core import security
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=security.JWT_EXPIRES_IN_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, security.JWT_SECRET_KEY, algorithm=security.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, security.JWT_SECRET_KEY, algorithms=[security.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
