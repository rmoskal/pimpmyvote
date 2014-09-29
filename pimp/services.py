from models import User
from core import Service


class UsersService(Service):
    __model__ = User

users = UsersService()