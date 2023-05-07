from datetime import datetime

from fastapi import HTTPException, Request

from .models import PlaylistToDB, PlaylistOut
from app.utils import get_first_result
from app.validation import PyObjectId


def create_playlist(request: Request, data):
    db = request.app.db
    user_id = PyObjectId(request.user.username)
    updated = datetime.utcnow()
    playlist_to_save = PlaylistToDB(title=data['title'], user_id=user_id, updated=updated)
    result = db.playlists.insert_one(playlist_to_save.dict())
    return result.inserted_id


def get_playlist_by_id(request: Request, playlist_id):
    db = request.app.db
    cursor = db.playlists.aggregate([
        {'$match': {'_id': playlist_id}},
        {'$unwind': {'path': '$video_ids', 'preserveNullAndEmptyArrays': True}},
        {'$lookup': {'from': 'videos', 'localField': 'video_ids', 'foreignField': '_id', 'as': 'videos'}},
        {'$facet': {'rootObj': [{'$limit': 1}], 'videos': [{'$group': {'_id': '$_id', 'videos': {'$push': {'$first': '$videos'}}}}]}},
        {'$replaceRoot': {'newRoot': {'$mergeObjects': [{'$first': '$rootObj'}, {'$first': '$videos'}]}}}
    ])
    raw_playlist = get_first_result(cursor)
    if not raw_playlist:
        raise HTTPException(status_code=404)
    validated_playlist = PlaylistOut(**raw_playlist).dict()
    return validated_playlist


def get_playlists(request):
    db = request.app.db
    playlists = db.playlists.find().limit(100)
    return playlists


def add_video_to_playlist(request: Request, playlist_id, video_id):
    db = request.app.db
    video_id = PyObjectId(video_id)
    db.playlists.update_one({'_id': playlist_id}, {'$push': {'video_ids': video_id}})


def remove_video_from_playlist(request: Request, playlist_id, video_index):
    db = request.app.db
    db.playlists.update_one({'_id': playlist_id}, {'$set': {f'video_ids.{video_index}': None}})
    db.playlists.update_one({'_id': playlist_id}, {'$pull': {'video_ids': None}})
