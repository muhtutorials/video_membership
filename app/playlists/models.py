from datetime import datetime

from pydantic import Field, validator

from app.videos.models import VideoOut
from app.validation import CustomBaseModel, PyObjectId, str_to_object_id, object_id_to_str


class PlaylistBase(CustomBaseModel):
    title: str


class PlaylistIn(PlaylistBase):
    pass


class PlaylistToDB(PlaylistBase):
    user_id: PyObjectId
    video_ids: PyObjectId = []
    updated: datetime
    _str_to_object_id = validator('user_id', allow_reuse=True)(str_to_object_id)


class PlaylistOut(PlaylistToDB):
    id: PyObjectId = Field(..., alias='_id')
    videos: list[VideoOut]

    _object_id_to_str = validator('id', 'user_id', allow_reuse=True)(object_id_to_str)


class VideoIndex(CustomBaseModel):
    index: int
