import uuid
from app.shortcuts import get_object_or_404
from app.video.extractor import extract_yt_id_from
from app.video.models import Video
from pydantic import BaseModel, validator, root_validator
from pydantic import BaseModel, root_validator

from app.playlist.models import Playlist


class CreatePlaylistSchema(BaseModel):
    title: str
    user_id: str
        

    @root_validator
    def validate_data(cls, values):
        user_id = values.get('user_id')
        title = values.get('title')

        existings = Playlist.objects.allow_filtering().filter(title=title, user_id=user_id)
        if existings.count() > 0:
            raise ValueError('Playlists name should be unique!')

        pl = Playlist.objects.create(title=title, user_id=user_id)
        return pl.as_data()


class PlaylistAddVideoSchema(BaseModel):
    url: str
    title: str
    user_id: uuid.UUID  # will be fetched from user session
    playlist_id: uuid.UUID # its the playlist models db_id

    @validator("url")
    def validate_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_yt_id_from(url)

        if not video_id:
            raise ValueError("Invalid video url.")

        return url
    
    @validator("playlist_id")
    def validate_playlist_id(cls, v, values, **kwargs):
        playlist_id = v
        playlists = Playlist.objects.filter(db_id=playlist_id)
        if playlists.count() == 0:
            get_object_or_404(Playlist, db_id=playlist_id)

        return playlist_id

    @root_validator
    def validate_data(cls, values):
        url = values.get('url')
        user_id = values.get('user_id')
        title = values.get('title')
        playlist_id = values.get('playlist_id')

        video = None
        created = False
        extra_data = {}

        if title is not None:
            extra_data = {
                'title': title
            }

        try:
            video, _ = Video.get_or_create(url=url, user_id=user_id, **extra_data)
        except Exception as error:
            raise ValueError('there is a problem with the link!')

        if video:
            playlist = Playlist.objects.get(db_id=playlist_id)
            playlist.add_videos(video_list = [video.video_id])
            playlist.save()

        return video.as_data()
