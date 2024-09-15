from typing import Union
from app.config import settings
import jwt


def decode_jwt_token(token: str) -> Union[dict, None]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except:
        return None