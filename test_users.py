import pytest

from app.auth.utils import create_user, delete_user
from app.auth.models import UserIn


def test_create_user():
    user_data = {'email': 'test@email.com', 'password': '123456'}
    user = UserIn(**user_data)
    create_user(user)
    # delete_user(user_data['email'])
