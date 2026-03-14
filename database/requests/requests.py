from dataclasses import dataclass, field

from . import users


@dataclass
class Users:
    @property
    def get_user(self):
        return users.get_user

    @property
    def get_all_alive_users(self):
        return users.get_all_alive_users

    @property
    def add_user(self):
        return users.add_user

    @property
    def change_role(self):
        return users.change_role

    @property
    def change_is_alive(self):
        return users.change_is_alive

    @property
    def change_name(self):
        return users.change_name


@dataclass
class Requests:
    users: Users = field(default_factory=Users)


requests = Requests()
