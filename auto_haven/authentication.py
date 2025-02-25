import os
from typing import Dict
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "TOKEN_EXPIRY_MINUTES": int(os.getenv("TOKEN_EXPIRY_MINUTES", "30")),
    "SECRET_KEY": os.getenv("JWT_SECRET_KEY") or os.urandom(32).hex(),
    "ALGORITHM": "HS256",
}


class AuthenticationHandler:
    def __init__(
        self,
        secret_key: str = CONFIG["SECRET_KEY"],
        expiry_minutes: int = CONFIG["TOKEN_EXPIRY_MINUTES"],
    ):
        self.security = HTTPBearer()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = secret_key
        self.expiry_minutes = expiry_minutes
        if not secret_key:
            raise ValueError(
                "Secret key must be provided via environment variable JWT_SECRET_KEY"
            )

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_auth_token(self, user_id: str, username: str) -> str:
        subject = f"{user_id}:{username}"
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.expiry_minutes),
            "iat": datetime.now(timezone.utc),
            "sub": subject,
        }
        try:
            return jwt.encode(payload, self.secret_key, algorithm=CONFIG["ALGORITHM"])
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create token: {str(e)}"
            )

    def decode_auth_token(self, token: str) -> Dict[str, str]:
        cleaned_token = token.strip("\"'")
        try:
            payload = jwt.decode(
                cleaned_token, self.secret_key, algorithms=[CONFIG["ALGORITHM"]]
            )
            sub = payload.get("sub")
            user_id, username = sub.split(":")
            return {"user_id": user_id, "username": username}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401, detail=f"Invalid token format or signature: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Token decoding error: {str(e)}"
            )

    async def authentication_wrapper(
        self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Dict[str, str]:
        if not auth.credentials:
            raise HTTPException(
                status_code=401, detail="No authentication token provided"
            )
        return self.decode_auth_token(auth.credentials)
