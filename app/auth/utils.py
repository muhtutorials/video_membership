from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError

from app.config import get_settings
from .models import UserToDB, UserOut, TokenData


settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS = 30


def create_user(db, data):
    user = db.users.find_one({'username': data['username']})
    if user:
        raise HTTPException(status_code=409, detail='Username already exists.')
    user = db.users.find_one({'email': data['email']})
    if user:
        raise HTTPException(status_code=409, detail='Email already exists.')
    ph = PasswordHasher()
    hashed_password = ph.hash(data['password'])
    user_to_save = UserToDB(username=data['username'], email=data['email'], hashed_password=hashed_password)
    result = db.users.insert_one(user_to_save.dict())
    return result.inserted_id


def authenticate_user(db, data):
    user = db.users.find_one({'username': data['username']})
    if not user:
        return False
    ph = PasswordHasher()
    try:
        ph.verify(user['hashed_password'], data['password'])
    except VerifyMismatchError:
        return False
    return user


def create_access_token(username):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {'sub': username, 'exp': expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(request):
    access_token = request.cookies.get('access_token')
    if access_token is None:
        return
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return
    username = payload.get('sub')
    if username is None:
        return
    token_data = TokenData(username=username)
    user = request.app.db.users.find_one({'username': token_data.username})
    if user is None:
        return
    return UserOut(**user).dict()


def delete_user(db, username):
    result = db.users.delete_one({'username': username})
    return result
