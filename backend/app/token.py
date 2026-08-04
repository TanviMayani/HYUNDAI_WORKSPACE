import os
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import traceback
from datetime import datetime, timedelta
from typing import Union, Any
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES") 
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") 
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

app = FastAPI()

def decodeJWT(jwtoken: str):
    """
    Decode a JWT token.

    Args:
        jwtoken (str): The JWT token to be decoded.

    Returns:
        dict: The decoded payload if the token is valid, otherwise None.
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=401, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=401, detail="Invalid token or expired token."
                )
            return credentials.credentials
        return None
        # else:
        #     raise HTTPException(status_code=401, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the validity of a JWT token.

        Args:
            jwtoken (str): The JWT token to be verified.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            payload = decodeJWT(jwtoken)
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.JWTError as e:  
            traceback.print_exc()
            return False


jwt_bearer = JWTBearer()

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    Create an access token.

    Args:
        subject (Union[str, Any]): The subject of the token.
        expires_delta (int, optional): The expiration time of the token in minutes. Defaults to None.

    Returns:
        str: The created JWT token.
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt
