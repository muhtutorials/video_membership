from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.authentication import AuthenticationMiddleware

from .auth.router import router as auth_router
from .backends import JWTCookieBackend
from .config import get_settings
from .exceptions import http_exception_handler, validation_exception_handler
from .playlists.router import router as playlist_router
from .search.router import router as search_router
from .utils import render
from .videos.router import router as videos_router
from .watch_events.router import router as watch_events_router

db_uri = get_settings().db_uri


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = MongoClient(db_uri)
    db = client.videomembership
    app.db = db
    yield
    client.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth_router)
app.include_router(videos_router)
app.include_router(watch_events_router)
app.include_router(playlist_router)
app.include_router(search_router)


@app.get('/', response_class=HTMLResponse)
async def home_view(request: Request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    return render(request, 'home.html')
