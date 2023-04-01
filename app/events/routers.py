from fastapi import Request
from fastapi.routing import APIRouter

from app.events.models import Event
from app.events.schemas import EventSchema
from app.users.decorators import login_required


router = APIRouter(
    prefix='/events'
)


@router.post('/playback', response_model=EventSchema)
@login_required
def save_video_playback_history(request: Request, event_data: EventSchema):

    cleaned_data = event_data.dict()
    data = cleaned_data.copy()
    data.update({
        'user_id': request.user.username
    })
    Event.objects.create(**data)

    return event_data
