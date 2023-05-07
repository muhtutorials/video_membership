from datetime import datetime

from pydantic import validator

from app.validation import CustomBaseModel, PyObjectId, str_to_object_id


class WatchEventBase(CustomBaseModel):
    host_id: str
    path: str | None
    start_time: float
    end_time: float
    duration: float
    complete: bool


class WatchEventIn(WatchEventBase):
    pass


class WatchEventToDB(WatchEventBase):
    user_id: PyObjectId
    created_at: datetime
    _str_to_object_id = validator('user_id', allow_reuse=True)(str_to_object_id)
