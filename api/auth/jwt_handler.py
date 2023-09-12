from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import time
from typing import Dict
from typing import Annotated
import jwt
from api.schemas.auth import Token

from config.config import Settings


def token_response(token: str):
    return token


secret_key = Settings().SECRET_KEY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def sign_jwt(user_id: str) -> Dict[str, str]:
    # Set the expiry time.
    payload = {"user_id": user_id, "expires": time.time() + 604800}
    return token_response(jwt.encode(payload, secret_key, algorithm="HS256"))


def decode_jwt(token: str) -> Token:
    decoded_token = jwt.decode(token.encode(), secret_key, algorithms=["HS256"])
    return decoded_token if decoded_token["expires"] >= time.time() else {}


async def get_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    user = Token(**decode_jwt(token))
    return user.user_id
