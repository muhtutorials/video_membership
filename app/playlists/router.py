from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.utils import login_required
from app.utils import check_if_htmx, redirect, render
from app.validation import validate_form, validate_path, ObjectIDModel
from app.videos.models import VideoIn
from app.videos.utils import get_or_create_video
from .models import PlaylistIn, VideoIndex
from .utils import create_playlist, get_playlist_by_id, get_playlists, add_video_to_playlist, remove_video_from_playlist

router = APIRouter(prefix='/playlists')


@router.get('/create', response_class=HTMLResponse)
@login_required
async def playlist_create_view(request: Request):
    return render(request, 'playlists/create.html')


@router.post('/create', response_class=HTMLResponse)
@login_required
async def playlist_create(request: Request):
    data, errors = await validate_form(request, PlaylistIn)
    if errors:
        return render(request, 'playlists/create.html', {'data': data, 'errors': errors}, status_code=400)
    playlist_id = create_playlist(request, data)
    return redirect(f'/playlists/{playlist_id}')


@router.get('/', response_class=HTMLResponse)
async def playlist_list(request: Request):
    playlists = get_playlists(request)
    return render(request, 'playlists/list.html', {'playlists': playlists})


@router.get('/{playlist_id}', response_class=HTMLResponse)
async def playlist_detail(request: Request, playlist_id: str):
    playlist_id = validate_path(ObjectIDModel, id=playlist_id)['id']
    playlist = get_playlist_by_id(request, playlist_id)
    return render(request, 'playlists/detail.html', {'playlist': playlist})


@router.get('/{playlist_id}/add-to-playlist', response_class=HTMLResponse)
@login_required
async def add_to_playlist_view(request: Request, playlist_id: str, is_htmx=Depends(check_if_htmx)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    return render(request, 'playlists/htmx/add_to_playlist.html', {'playlist_id': playlist_id})


@router.post('/{playlist_id}/add-to-playlist', response_class=HTMLResponse)
@login_required
async def add_to_playlist(request: Request, playlist_id: str, is_htmx=Depends(check_if_htmx)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    data, errors = await validate_form(request, VideoIn)
    playlist_id = validate_path(ObjectIDModel, id=playlist_id)['id']
    if errors:
        return render(
            request,
            'playlists/htmx/add_to_playlist.html',
            {'data': data, 'errors': errors, 'playlist_id': playlist_id}
        )
    video, _ = get_or_create_video(request, data)
    add_video_to_playlist(request, playlist_id, video['id'])
    return render(request, 'playlists/htmx/link.html', {'path': f'/videos/{video["id"]}', 'title': data['title']})


@router.post('/{playlist_id}/delete', response_class=HTMLResponse)
@login_required
async def remove_from_playlist(
        request: Request,
        playlist_id: str,
        is_htmx=Depends(check_if_htmx)
):
    if not is_htmx:
        raise HTTPException(status_code=400)
    playlist_id = validate_path(ObjectIDModel, id=playlist_id)['id']
    data, errors = await validate_form(request, VideoIndex)
    if errors:
        return HTMLResponse('An error occurred')
    remove_video_from_playlist(request, playlist_id, data['index'])
    return HTMLResponse('Deleted')
