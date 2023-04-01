from uuid import uuid1

from app.users.models import User


def user_exist(user_id: uuid1, _return: bool=True, raise_exception: bool=False):
    exist = False

    users = User.objects.filter(user_id=user_id).allow_filtering()

    if users.count() == 0:
        return exist, None
    
    return exist, users.first() if _return else exist, None