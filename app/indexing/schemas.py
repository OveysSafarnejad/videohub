import uuid
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional


class VideoIndexSchema(BaseModel):
    objectID: str = Field(alias='video_id')
    objectType: str = "Video"
    title: Optional[str]
    path: str = Field(alias='video_id')
    # related -> playlist names

    @validator("path")
    def set_path(cls, v, values, **kwargs):
        video_id = v
        return f"/videos/{video_id}"


class PlaylistIndexSchema(BaseModel):
    objectID: uuid.UUID = Field(alias='db_id')
    objectType: str = "Playlist"
    title: Optional[str]
    path: str = Field(default='/')
    # related -> host_ids -> Video Title

    @root_validator
    def set_defaults(cls, values):
        objectID = values.get('objectID')
        values['objectID'] = str(objectID)
        values['path'] = f"/playlists/{objectID}"
        return values
