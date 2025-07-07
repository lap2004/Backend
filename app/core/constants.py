# app/core/constants.py

from enum import Enum

class Role(str, Enum):
    guest = "guest"
    student = "student"
    admin = "admin"

class BotType(str, Enum):
    admission = "admission"
    student = "student"
