from datetime import datetime

from fastapi import Request

from app.utils import get_first_result
from app.validation import PyObjectId
from .models import WatchEventToDB


def create_watch_event(request: Request, data):
    db = request.app.db
    user_id = PyObjectId(request.user.username)
    created_at = datetime.utcnow()
    watch_event_to_save = WatchEventToDB(user_id=user_id, created_at=created_at, **data.dict())
    result = db.watch_events.insert_one(watch_event_to_save.dict())
    return result.inserted_id


def get_video_start_time(request, host_id):
    if not request.user.is_authenticated:
        return 0
    user_id = PyObjectId(request.user.username)
    cursor = request.app.db.watch_events\
        .find({'host_id': host_id, 'user_id': user_id})\
        .sort('created_at', -1)\
        .limit(1)
    watch_event = get_first_result(cursor)
    start_time = watch_event['end_time'] if watch_event and not watch_event['complete'] else 0
    return start_time
