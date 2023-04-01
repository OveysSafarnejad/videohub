import pytest

from app.users.models import User
from app import db


@pytest.fixture(scope='module')
def setup():
    session = db.get_session()
    yield session

    users = User.objects.filter(email='test@mail.com')
    if users:
        users.delete()

def test_create_user(setup):
    User.create_user(email='test@mail.com', password='abc123')


def test_duplicate_email(setup):
    with pytest.raises(Exception):
        User.create_user(email='test@mail.com', password='abc123')


def test_invalid_email(setup):
    with pytest.raises(Exception):
        User.create_user(email='test@mail')


def test_password_is_hashed(setup):
    user = User.objects.get(email='test@mail.com')
    assert user.password is not 'abc123'


def test_verify_password(setup):
    user = User.objects.get(email='test@mail.com')
    assert user.verify_password('abc123') == True