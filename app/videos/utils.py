from fastapi import Request

from .models import VideoToDB, VideoOut, VideoListOut
from app.validation import PyObjectId


def get_or_create_video(request: Request, data):
    created = False
    db = request.app.db
    user_id = PyObjectId(request.user.username)
    video = db.videos.find_one({'host_id': data['host_id'], 'user_id': user_id})
    if video:
        video = VideoOut(**video).dict()
        return video, created
    video_to_save = VideoToDB(url=data['url'], title=data['title'], host_id=data['host_id'], user_id=user_id)
    result = db.videos.insert_one(video_to_save.dict())
    video = VideoOut(_id=result.inserted_id, **video_to_save.dict()).dict()
    created = True
    return video, created


def update_video(request: Request, video_id, data):
    db = request.app.db
    user_id = PyObjectId(request.user.username)
    db.videos.update_one({'_id': video_id, 'user_id': user_id}, {'$set': {**data}})


def delete_video(request: Request, video_id):
    db = request.app.db
    db.videos.delete_one({'_id': video_id})


def get_videos(request):
    db = request.app.db
    raw_videos = db.videos.find().limit(100)
    validated_videos = VideoListOut(videos=list(raw_videos)).dict()['videos']
    return validated_videos
