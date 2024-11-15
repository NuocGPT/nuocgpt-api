from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_handler import decode_jwt
from config.constants import ErrorMessage


def verify_jwt(jwtoken: str) -> bool:
    isTokenValid: bool = False

    payload = decode_jwt(jwtoken)
    if payload:
        isTokenValid = True
    return isTokenValid


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
                    status_code=403, detail=ErrorMessage.TOKEN_INVALID_OR_EXPIRED
                )

            if not verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail=ErrorMessage.TOKEN_INVALID_OR_EXPIRED
                )

            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail=ErrorMessage.TOKEN_INVALID_OR_EXPIRED)
