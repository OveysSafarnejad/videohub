from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    validator,
    root_validator
)

from app.users.auth.backends import (
    validate_user,
    login
)
from app.users.models import User


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: SecretStr
    token: str = None

    @root_validator
    def authenticate(cls, values):
        email = values.get('email') or None
        password = values.get('password') or None

        if email is None or password is None:
            raise ValueError('authentication failed!')

        password = password.get_secret_value()
        user = validate_user(email, password)
        if not user:
            raise ValueError('authentication failed!')

        token = login(user=user)

        return dict(token=token)


class UserSignupSchema(BaseModel):
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr


    @validator('email')
    def check_email(cls, v, values, **kwargs):
        if User.objects.filter(email=v).count() > 0 :
            raise ValueError('email address is not available!')

        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        password = values.get('password')
        password_confirm = v

        if password != password_confirm:
            raise ValueError('passwords don\'t match!')

        return v



