import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import  HTMLResponse

from app.events.models import Event
from app.utils.utility import validate_schema
from app.shortcuts import get_object_or_404, redirect, render, is_htmx
from app.users.decorators import login_required
from app.video.models import Video
from app.video.schemas import CreateVideoSchema, EditVideoSchema

router = APIRouter(
    prefix='/videos'
)


@router.get('/', response_class=HTMLResponse)
@login_required
def videos(request: Request):
    context = {
        'videos': list(Video.objects.all())
    }
    return render(request=request, template='videos/list.html', context=context)


@router.get('/create', response_class=HTMLResponse)
@login_required
def video_create_view(request: Request, is_htmx=Depends(is_htmx), playlist_id: Optional[uuid.UUID]=None):

    if is_htmx:
        return render(request=request, template='videos/htmx/create.html')
    return render(request=request, template='videos/create.html')


@router.post('/create', response_class=HTMLResponse)
@login_required
def video_create_post_view(request: Request, is_htmx=Depends(is_htmx), url: str = Form(...), title: str = Form(...)):

    raw_data = {
        'url': url,
        'user_id': request.user.username,
        'title': title
    }

    data, errors = validate_schema(raw_data=raw_data, SchemaModel=CreateVideoSchema)

    redirect_url = data.get('path') or '/videos/create'
    context = {
        "data": data,
        "errors": errors,
        "title": title,
        "url": url,
    }

    if is_htmx:
        if len(errors) > 0:
            return render(request, "/videos/htmx/create.html", context=context)

        context = {
            "path": redirect_url,
            "title": title
        }
        return render(request, template="/videos/htmx/link.html", context=context)

    if errors:
        context = {
            "errors": errors
        }
        return render(request, template='/videos/create.html', context=context, status_code=status.HTTP_400_BAD_REQUEST)

    return redirect(path=redirect_url)



@router.get('/{video_id}', response_class=HTMLResponse)
@login_required
def video_detail(request: Request, video_id: str):
    video = get_object_or_404(Video, video_id=video_id)
    context = {
        'instance': video,
        'start_time': Event.get_resume_time(video_id,  request.user.username)
    }

    return render(request, template='videos/detail.html', context=context, status_code=status.HTTP_200_OK)


@router.get('/{video_id}/edit', response_class=HTMLResponse)
@login_required
def video_edit_view(request: Request, video_id: str, is_htmx=Depends(is_htmx)):

    video = get_object_or_404(Video, video_id=video_id)
    context = {
        'video':  video
    }
    return render(request=request, template='videos/edit.html', context=context)


@router.post('/{video_id}/edit', response_class=HTMLResponse)
@login_required
def video_edit_post_view(
    request: Request,
    video_id: str,
    is_htmx=Depends(is_htmx),
    url: str = Form(...),
    title: str = Form(...)
):

    raw_data = {
        'url': url,
        'title': title
    }

    data, errors = validate_schema(
        raw_data=raw_data, SchemaModel=EditVideoSchema)

    if errors:
        context = {
            "errors": errors
        }
        return render(request, template='/videos/edit.html', context=context, status_code=status.HTTP_400_BAD_REQUEST)
    obj = get_object_or_404(Video, video_id=video_id)

    obj.title = data.get("title") or obj.title
    obj.url = obj.update_video_url(url, save_instance=True)

    context = {
        'video':  obj
    }
    return render(request=request, template='videos/edit.html', context=context)


@router.get('/{video_id}/hx-edit', response_class=HTMLResponse)
@login_required
def video_hx_edit_view(request: Request, video_id: str, is_htmx=Depends(is_htmx)):

    video = get_object_or_404(Video, video_id=video_id)
    context = {
        'video':  video
    }
    return render(request=request, template='videos/htmx/edit.html', context=context)


@router.post('/{video_id}/hx-edit', response_class=HTMLResponse)
@login_required
def video_hx_edit_post_view(
    request: Request,
    video_id: str,
    is_htmx=Depends(is_htmx),
    url: str = Form(...),
    title: str = Form(...),
    delete: Optional[bool] = Form(default=False)
):

    raw_data = {
        'url': url,
        'title': title,
        'user_id': request.user.username
    }
    obj = get_object_or_404(Video, video_id=video_id)
    if delete:
        obj.delete()
        return HTMLResponse('Item Deleted')

    data, errors = validate_schema(
        raw_data=raw_data, SchemaModel=EditVideoSchema)

    if errors:
        context = {
            "errors": errors
        }
        return render(request, template='/videos/htmx/edit.html', context=context, status_code=status.HTTP_400_BAD_REQUEST)



    obj.title = data.get("title") or obj.title
    obj.url = obj.update_video_url(url, save_instance=True)

    context = {
        'video':  obj
    }
    return render(request=request, template='videos/htmx/video-inline-edit.html', context=context)
