from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse

from app.decorators import htmx_required
from app.playlist.models import Playlist
from app.playlist.schemas import CreatePlaylistSchema, PlaylistAddVideoSchema
from app.shortcuts import get_object_or_404, is_htmx, redirect, render
from app.users.decorators import login_required
from app.utils.utility import validate_schema


router = APIRouter(
    prefix='/playlists'
)


@router.get('/', response_class=HTMLResponse)
@login_required
def playlists(request: Request):
    context = {
        'playlists': list(Playlist.objects.all())
    }
    return render(request=request, template='playlists/list.html', context=context)


@router.get('/create', response_class=HTMLResponse)
@login_required
def playlist_create_view(request: Request):
    return render(request=request, template='playlists/create.html', context={}, status_code=status.HTTP_200_OK)


@router.post('/create', response_class=HTMLResponse)
@login_required
def playlist_create_post_view(request: Request, title: str = Form(...)):
    raw_data = {
        'user_id': request.user.username,
        'title': title
    }

    data, errors = validate_schema(
        raw_data=raw_data, SchemaModel=CreatePlaylistSchema)
    if errors:
        context = {
            "errors": errors
        }
        return render(request, template='/playlists/create.html', context=context, status_code=status.HTTP_400_BAD_REQUEST)

    redirect_url = data.get('path') or '/playlists/create'
    return redirect(path=redirect_url)


@router.get('/{db_id}', response_class=HTMLResponse)
@login_required
def playlist_detail(request: Request, db_id: uuid.UUID):
    pl = get_object_or_404(Playlist, db_id=db_id)
    context = {
        'instance': pl
    }

    return render(request, template='playlists/detail.html', context=context, status_code=status.HTTP_200_OK)


@router.get('/{db_id}/add-video', response_class=HTMLResponse)
@login_required
def playlist_add_video_get_view(request: Request, db_id: uuid.UUID, is_htmx=Depends(is_htmx)):

    context = {
        'db_id': db_id
    }
    return render(request=request, template='playlists/htmx/add-video.html', context=context)


@router.post('/{db_id}/add-video', response_class=HTMLResponse)
@login_required
def playlist_add_video_post_view(
    request: Request,
    db_id: uuid.UUID,
    is_htmx=Depends(is_htmx),
    url: str = Form(...),
    title: str = Form(...)
):

    raw_data = {
        'url': url,
        'user_id': request.user.username,
        'title': title,
        'playlist_id': db_id
    }

    data, errors = validate_schema(
        raw_data=raw_data, SchemaModel=PlaylistAddVideoSchema
    )

    redirect_url = data.get('path') or f'/playlists/{db_id}'
    context = {
        'data': data,
        'errors': errors,
        'title': title,
        'url': url,
        'db_id': db_id
    }

    if len(errors) > 0:
        return render(request, "playlists/htmx/add-video.html", context=context)

    context = {
        'path': redirect_url,
        'title': title
    }
    return render(request, template="/videos/htmx/link.html", context=context)


@router.post('/{db_id}/videos/{video_id}/delete', response_class=HTMLResponse)
@login_required
def playlist_remove_video_view(
    request: Request,
    db_id: uuid.UUID,
    video_id: str
):
    try:
        pl = get_object_or_404(Playlist, db_id=db_id)
    except:
        raise Exception()

    pl_videos = pl.video_ids
    pl_videos.remove(video_id)
    pl.add_videos(video_list=pl_videos, replace_all=True)

    return HTMLResponse('deleted')
