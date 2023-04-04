import uuid

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app.config import get_settings
from app.users.exceptions import InvalidEmailAddressException, UserAlreadyExistException
from app.utils.security import (
    generate_hash_from,
    verify_hash
)
from app.utils.validators import _validate_email

settings = get_settings()

class User(Model):
    __keyspace__ = settings.keyspace

    email = columns.Text(primary_key=True)
    user_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    password = columns.Text()

    def __repr__(self):
        return f"User(email={self.email}, user_id={self.user_id})"

    def __str__(self):
        return self.__repr__()

    def set_password(self, raw_password, commit=False):

        hashed_pw = generate_hash_from(raw_password=raw_password)
        self.password = hashed_pw
        if commit:
            self.save()

        return True

    def verify_password(self, raw_password):

        hashed = self.password
        verified, _ = verify_hash(hashed, raw_password)

        return verified


    @staticmethod
    def create_user(email,  password=None):
        if len(User.objects.filter(email=email)):
            raise UserAlreadyExistException('User already exist!')

        valid, message, email = _validate_email(email=email)
        if not valid:
            raise InvalidEmailAddressException(f'Email is not valid: {message}')

        obj = User(email=email)
        obj.set_password(password)
        return obj.save()