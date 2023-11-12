from enum import Enum

VALID_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
]

USER_GROUPS = (
    'administrator',
    'manager',
    'supervisor'
    'employee',
)


class UserGroups(Enum):
    ADMINISTRATOR = 'administrator'
    MANAGER = 'manager'
    SUPERVISOR = 'supervisor'
    EMPLOYEE = 'employee'


class AuthorisationError(Enum):
    UNAUTHORIZED = 1
    FORBIDDEN = 2
