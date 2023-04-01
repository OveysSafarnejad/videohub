import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app import config

settings = config.get_settings()

class Event(Model):
    __keyspace__ = settings.keyspace

    video_id = columns.Text(primary_key=True)
    user_id = columns.UUID(primary_key=True)
    path = columns.Text()
    event_id = columns.TimeUUID(primary_key=True, clustering_order="DESC", default=uuid.uuid1)


    start_time = columns.Double()
    end_time = columns.Double()
    duration = columns.Double()
    completed = columns.Boolean(default=False)


    @staticmethod
    def get_resume_time(video_id, user_id):
        start_time = 0 
        event = Event.objects.allow_filtering().filter(video_id=video_id, user_id=user_id).first()

        if event:
            if not event.completed and not (event.duration * 0.98) < event.end_time:
                return event.end_time
            
        return start_time
