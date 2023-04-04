from pydantic import BaseModel, validator, root_validator
from app.users.exceptions import (
    UserDoesNotExistException
)
from app.video.exceptions import InvalidUrlException, VideoUlreadyAddedException

from app.video.models import Video
from app.video.extractor import extract_yt_id_from

class CreateVideoSchema(BaseModel):
    url: str
    title: str
    user_id: str # will be fetched from user session

    @validator("url")
    def validate_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_yt_id_from(url)

        if not video_id:
            raise ValueError("Invalid video url.")

        return url

    @root_validator
    def validate_data(cls, values):
        url = values.get('url')
        user_id = values.get('user_id')
        title = values.get('title')
        try:
            video = Video.add_video(url=url, user_id=user_id)
        except UserDoesNotExistException:
            raise ValueError('user account not found!')
        except InvalidUrlException:
            raise ValueError('url is not valid!')
        except VideoUlreadyAddedException:
            raise ValueError('video already added!!')
        except:
            raise ValueError('there is some problems with your account, try another url or call site administration!')


        video.title = title
        video.save()
        return video.as_data()


class EditVideoSchema(BaseModel):
    url: str
    title: str

    @validator("url")
    def validate_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_yt_id_from(url)

        if not video_id:
            raise ValueError("Invalid video url.")

        return url
