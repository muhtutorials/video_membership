from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.watch_events.utils import get_video_start_time
from app.utils import render, redirect, get_item_or_404, login_required, check_if_htmx
from app.validation import validate_form, validate_path, ObjectIDModel
from .models import VideoIn, VideoOut
from .utils import get_or_create_video, get_videos, update_video, delete_video

router = APIRouter(prefix='/videos')


@router.get('/create', response_class=HTMLResponse)
@login_required
async def video_create_view(request: Request):
    return render(request, 'videos/create.html')


@router.post('/create', response_class=HTMLResponse)
@login_required
async def video_create(request: Request):
    data, errors = await validate_form(request, VideoIn)
    if errors:
        return render(request, 'videos/create.html', {'data': data, 'errors': errors}, status_code=400)
    video, created = get_or_create_video(request, data)
    if created:
        return redirect(f'/videos/{video["id"]}')
    errors = [{'loc': ['url'], 'msg': 'Video already exists'}]
    return render(request, 'videos/create.html', {'data': data, 'errors': errors}, status_code=400)


@router.get('/', response_class=HTMLResponse)
async def video_list(request: Request):
    videos = get_videos(request)
    return render(request, 'videos/list.html', {'videos': videos})


@router.get('/{video_id}', response_class=HTMLResponse)
async def video_detail(request: Request, video_id: str):
    data = validate_path(ObjectIDModel, id=video_id)
    video = get_item_or_404(request.app.db.videos, VideoOut, _id=data['id'])
    start_time = get_video_start_time(request, video['host_id'])
    return render(request, 'videos/detail.html', {'video': video, 'start_time': start_time})


@router.get('/{video_id}/edit', response_class=HTMLResponse)
@login_required
async def video_edit_view(request: Request, video_id: str):
    data = validate_path(ObjectIDModel, id=video_id)
    video = get_item_or_404(request.app.db.videos, VideoOut, _id=data['id'])
    return render(request, 'videos/edit.html', {'video': video})


@router.post('/{video_id}/edit', response_class=HTMLResponse)
@login_required
async def video_edit(request: Request, video_id: str):
    video_id = validate_path(ObjectIDModel, id=video_id)['id']
    data, errors = await validate_form(request, VideoIn)
    if errors:
        return render(request, 'videos/edit.html', {'video': data, 'errors': errors}, status_code=400)
    update_video(request, video_id, data)
    return redirect(f'/videos/{video_id}')


@router.get('/{video_id}/hx-edit', response_class=HTMLResponse)
@login_required
async def video_hx_edit_view(request: Request, video_id: str, is_htmx=Depends(check_if_htmx)):
    data = validate_path(ObjectIDModel, id=video_id)
    video = get_item_or_404(request.app.db.videos, VideoOut, _id=data['id'])
    return render(request, 'videos/htmx/edit.html', {'video': video})


@router.post('/{video_id}/hx-edit', response_class=HTMLResponse)
@login_required
async def video_hx_edit(request: Request, video_id: str, delete: Annotated[str | None, Form()] = None):
    video_id = validate_path(ObjectIDModel, id=video_id)['id']
    if delete:
        delete_video(request, video_id)
        return HTMLResponse('Video Deleted')
    data, errors = await validate_form(request, VideoIn)
    if errors:
        return render(request, 'videos/edit.html', {'video': data, 'errors': errors}, status_code=400)
    update_video(request, video_id, data)
    data['id'] = video_id
    return render(request, 'videos/htmx/link.html', {'video': data})
