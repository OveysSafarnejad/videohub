import datetime

from jose import (
    ExpiredSignatureError,
    jwt
)

from app import config
from app.users.exceptions import LoginRequiredException
from app.users.models import User


settings = config.get_settings()


def validate_user(email: str, password: str):
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print('user does not exist!')
    except User.MultipleObjectsReturned:
        # centry capture
        user = User.objects.filter(email=email).first()
    
    if not user.verify_password(password):
        print('password does not match!')
    
    return user


def login(user: User, expires_after=settings.token_expiration_time):
    

    payload = {
        "user_id": f"{user.user_id}",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_after)
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    return token


def verify_user_by(token: str):

    decoded_from_jwt = {}
    try:
        decoded_from_jwt = jwt.decode(
            token=token, key=settings.secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as error:
        print(error)
        decoded_from_jwt = {}

    if 'user_id' not in decoded_from_jwt:
        return None

    return decoded_from_jwt
