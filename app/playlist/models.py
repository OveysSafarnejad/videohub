import uuid
from datetime import datetime

from cassandra.cqlengine import columns
from cassandra.cqlengine.management import Model

from app import config
from app.video.models import Video


settings = config.get_settings()


class Playlist(Model):
    __keyspace__ = settings.keyspace

    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    video_ids = columns.List(value_type=columns.Text)
    user_id = columns.UUID()
    title = columns.Text()
    updated = columns.DateTime(default=datetime.utcnow())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Playlist(title={self.title})"

    def as_data(self):
        data = {
            'title': self.title,
            '#items': len(self.video_ids),
            'path': self.path,
        }

        return data

    @property
    def path(self):
        return f'/playlists/{self.db_id}'

    def add_videos(self, video_list: list, replace_all: bool=False):
        # TODO:
        # video_list items should be validated before assignment

        if replace_all:
            self.video_ids = video_list
        else:
            self.video_ids.extend(video_list)

        self.updated = datetime.utcnow()

        self.save()

    def get_videos(self):
        playlist_videos = []
        for video in self.video_ids:
            try:
                video_obj = Video.objects.get(video_id=video)
            except Video.DoesNotExist:
                video_obj = None
            
            if video_obj:
                playlist_videos.append(video_obj)
                
        return playlist_videos
