from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer

from app.validation import validate_form
from app.utils import render, redirect, login_required
from .models import UserSignUp, UserSignIn, Token
from .utils import create_user, authenticate_user, create_access_token

router = APIRouter(prefix='/auth')

# This dependency will go and look in the request for that Authorization header,
# check if the value is Bearer plus some token, and will return the token as a str
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.get('/signup', response_class=HTMLResponse)
async def signup_view(request: Request):
    return render(request, 'auth/signup.html')


@router.post('/signup', response_class=HTMLResponse)
async def signup(request: Request):
    data, errors = await validate_form(request, UserSignUp)
    if errors:
        return render(request, 'auth/signup.html', {'data': data, 'errors': errors}, status_code=400)
    create_user(request.app.db, data)
    return redirect('/auth/signin')


@router.get('/signin', response_class=HTMLResponse)
async def signin_view(request: Request):
    return render(request, 'auth/signin.html')


@router.post('/signin', response_model=Token)
async def get_access_token(request: Request, next: str | None = None):
    data, errors = await validate_form(request, UserSignIn)
    if not errors:
        user = authenticate_user(request.app.db, data)
        if not user:
            errors = [{'loc': ['credentials_error'], 'msg': 'Invalid username or password'}]
        else:
            access_token = create_access_token(user['username'])
            return redirect(next if next else '/', cookies={'access_token': access_token})
    return render(request, 'auth/signin.html', {'data': data, 'errors': errors}, status_code=400)


@router.get('/signout', response_class=HTMLResponse)
@login_required
async def signout_view(request: Request):
    return render(request, 'auth/signout.html')


@router.post('/signout', response_class=HTMLResponse)
async def signout(request: Request):
    return redirect('/', end_session=True)
