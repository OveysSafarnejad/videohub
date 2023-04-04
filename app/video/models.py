import uuid
from cassandra.cqlengine.management import Model, columns
from cassandra.cqlengine.query import (
    MultipleObjectsReturned,
    DoesNotExist
)

from app.config import get_settings
from app.shortcuts import templates
from app.users.exceptions import UserDoesNotExistException
from app.users import service as user_services
from app.video.exceptions import InvalidUrlException, VideoUlreadyAddedException
from app.video.extractor import extract_yt_id_from



settings = get_settings()


class Video(Model):
    __keyspace__ = settings.keyspace
    video_id = columns.Text(primary_key=True)
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    title = columns.Text()
    user_id = columns.UUID()
    host_service = columns.Text(default='youtube')
    url = columns.Text()


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Video(video_id={self.video_id})"

    def render(self):
        template = f'videos/renderers/{self.host_service}.html'
        t = templates.get_template(template)
        context = {
            'video_id': self.video_id
        }

        return t.render(context)

    def as_data(self):
        data = {
            f'{self.host_service}_id': self.video_id,
            'path': self.path,
            'title': self.title
        }

        return data

    @property
    def path(self):
        return f'/videos/{self.video_id}'

    @staticmethod
    def get_or_create(url, user_id, **kwargs):

        video_id = extract_yt_id_from(url)
        created = False

        try:
            video_object = Video.objects.get(video_id=video_id)
        except DoesNotExist:
            video_object = Video.add_video(url=url, user_id=user_id)
            created = True
        except MultipleObjectsReturned:
            video_object = Video.objects.allow_filtering().filter(
                video_id=video_id, user_id=user_id).first()
        except Exception as error:
            raise Exception("there is some error with priveded url!")

        return video_object, created


    def update_video_url(self, url, save_instance = False):
        video_id = extract_yt_id_from(url)
        if video_id is None:
            raise InvalidUrlException('Invalid url!')

        self.url = url
        self.video_id = video_id
        if save_instance:
            self.save()
        return url

    @staticmethod
    def add_video(url, user_id):
        host_id = extract_yt_id_from(url)
        if host_id is None:
            raise InvalidUrlException('Invalid url!')

        user_exist = user_services.user_exist(
            user_id=user_id,
            _return=False,
            raise_exception=False
        )

        if not user_exist:
            raise UserDoesNotExistException('User does not exist!')

        existings = Video.objects.allow_filtering().filter(
            user_id=user_id, video_id=host_id)
        if existings.count() > 0 :
            raise VideoUlreadyAddedException('Video already added!')

        video = Video.create(video_id=host_id, user_id=user_id, url=url)

        return video



