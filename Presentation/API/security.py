import secrets
from fastapi import Header, HTTPException
from Presentation.API.settings import get_settings


def require_access(authorization: str = Header(default='')):
    token = get_settings().api_token
    if token and not secrets.compare_digest(authorization, 'Bearer ' + token):
        raise HTTPException(401, 'Token de acesso inválido', headers={'WWW-Authenticate': 'Bearer'})
