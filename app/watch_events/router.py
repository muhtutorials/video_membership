from fastapi import APIRouter, Request

from app.utils import login_required
from .models import WatchEventIn
from .utils import create_watch_event

router = APIRouter(prefix='/watch-events')


@router.post('/')
@login_required
async def watch_event(request: Request, data: WatchEventIn):
    create_watch_event(request, data)
    return {'status': 'success'}
