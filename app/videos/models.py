from urllib.parse import parse_qs, urlparse

from pydantic import Field, validator

from app.validation import CustomBaseModel, PyObjectId, object_id_to_str, str_to_object_id


def extract_video_id(url):
    # Source: https://stackoverflow.com/a/54383711
    # Examples:
    # - http://youtu.be/nNpvWBuTfrc
    # - http://www.youtube.com/watch?v=nNpvWBuTfrc&feature=feedu
    # - http://www.youtube.com/embed/nNpvWBuTfrc
    # - http://www.youtube.com/v/nNpvWBuTfrc?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/':
            return query.path.split('/')[1]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
        # # below is optional for playlists
        # if query.path[:9] == '/playlist':
        #     return parse_qs(query.query)['list'][0]
    return None


class VideoBase(CustomBaseModel):
    url: str
    host_id: str | None
    title: str

    @validator('host_id', always=True)
    def set_host_id(cls, _, values, **kwargs):
        if values.get('url'):
            host_id = extract_video_id(values['url'])
            if host_id:
                return host_id
            raise ValueError('Invalid URL')
        return None


class VideoIn(VideoBase):
    pass


class VideoToDB(VideoIn):
    user_id: PyObjectId
    _str_to_object_id = validator('user_id', allow_reuse=True)(str_to_object_id)


class VideoOut(VideoToDB):
    id: PyObjectId = Field(..., alias='_id')

    _object_id_to_str = validator('id', 'user_id', allow_reuse=True)(object_id_to_str)


class VideoListOut(CustomBaseModel):
    videos: list[VideoOut]
