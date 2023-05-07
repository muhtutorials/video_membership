from pydantic import Field, validator

from app.validation import CustomBaseModel, PyObjectId, object_id_to_str


class Index(CustomBaseModel):
    objectID: PyObjectId = Field(..., alias='_id')
    title: str

    _object_id_to_str = validator('objectID', allow_reuse=True)(object_id_to_str)


class VideoIndex(Index):
    type = 'video'


class PlaylistIndex(Index):
    type = 'playlist'
