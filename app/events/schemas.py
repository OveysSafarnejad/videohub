from typing import Optional
from pydantic import BaseModel


class EventSchema(BaseModel):
    video_id: str
    start_time: float
    end_time: float
    duration: float
    completed: bool
    path: Optional[str]
    