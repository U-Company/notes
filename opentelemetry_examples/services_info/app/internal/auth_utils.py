import random
import string
from datetime import timedelta, datetime

import jwt
from fastapi import Depends, HTTPException
from jwt import ExpiredSignatureError, PyJWTError
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from loguru import logger

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60
SECRET_KEY = "NITI vary secret key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def verify_password(login, password):
    if login == password:
        bad_password = False
    else:
        bad_password = True
    return bad_password


async def get_user_password_hash(username: str):
    hash = generate_password_hash(username)
    return hash


async def authenticate_user(username: str, password: str):
    if username == password:
        bad_password = False
    else:
        bad_password = True
    if bad_password:
        return False
    hash = await get_user_password_hash(username)
    return {'username': username, "hash": hash}


async def create_access_token(*, secret_key: str, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def make_token_for_user(user, secret_key):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    postfix = "".join(random.sample(string.ascii_letters, 2))
    access_token = await create_access_token(secret_key=secret_key,
        data={"sub": user['username'], "jti": f"{user['hash']}{postfix}"}, expires_delta=access_token_expires
    )
    token = Token(access_token=access_token, token_type="bearer")
    return token


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        jti: str = payload.get("jti")
        if jti is None:
            raise credentials_exception
    except ExpiredSignatureError as err:
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"{err}.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception
    except PyJWTError as err:
        logger.debug(f"{err}")
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"{err}.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception
    user_password_hash = await get_user_password_hash(username=username)
    if user_password_hash is None:
        raise credentials_exception
    token_hash = jti[:-2]
    is_good_hash = check_password_hash(token_hash, username)
    if is_good_hash:
        return username
    raise credentials_exception