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
    ADMINISTRATOR = 'Administrator'
    MANAGER = 'Manager'
    SUPERVISOR = 'Supervisor'
    EMPLOYEE = 'Employee'


class AuthorisationError(Enum):
    UNAUTHORIZED = 1
    FORBIDDEN = 2
