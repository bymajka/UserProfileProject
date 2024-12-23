from typing import Annotated, Optional
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from .logic import verify_password

_security = HTTPBasic()


def authenticated_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(_security)],
) -> Optional[str]:
    if verify_password(credentials.username, credentials.password):
        return credentials.username
    return None
