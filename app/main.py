from typing import Optional
from cassandra.cqlengine.management import sync_table
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from app import db
from app.events.models import Event
from app.events.routers import router as event_router
from app.indexing.client import search_index, update_index
from app.playlist.routers import router as playlist_router
from app.playlist.models import Playlist
from app.shortcuts import render
from app.users.auth.jwt_backend import JwtAuthenticationBackend 
from app.users.models import User
from app.users.routers import router as user_router
from app.video.models import Video
from app.video.routers import router as video_router


# %% configuration

app = FastAPI()
app.add_middleware(middleware_class=AuthenticationMiddleware, backend=JwtAuthenticationBackend())
app.include_router(user_router)
app.include_router(video_router)
app.include_router(event_router)
app.include_router(playlist_router)

# this should be placed right after the app initialization because of circular imports
from app.handlers import * # noqa

DATABASE_SESSION = None


# %% startup

@app.on_event("startup")
def on_startup():
    global DATABASE_SESSION
    DATABASE_SESSION = db.get_session()
    sync_table(User)
    sync_table(Video)
    sync_table(Event)
    sync_table(Playlist)


# %% apis

@app.get("/", response_class=HTMLResponse)
# @requires(scopes=['ccc'])
def home_page(request: Request):
    if request.user.is_authenticated:
        user = request.user
        return render(request=request, template='dashboard.html', context={"user": user})

    else:
        return redirect('/auth/login')
    

@app.post('/update-index', response_class=HTMLResponse)
def htmx_update_index_view(request: Request):
    count = update_index()
    return HTMLResponse(f"({count}) Refreshed")


@app.get("/search", response_class=HTMLResponse)
def search_detail_view(request: Request, q: Optional[str] = None):
    query = None
    context = {}
    if q is not None:
        query = q
        results = search_index(query)
        hits = results.get('hits') or []
        num_hits = results.get('nbHits')
        context = {
            "query": query,
            "hits": hits,
            "num_hits": num_hits
        }

    return render(request, "/search/detail.html", context=context)
