
import jwt
from muddery.worldeditor.settings import SETTINGS


def generate_token():
    return jwt.encode({}, SETTINGS.WORLD_EDITOR_SECRET)


def check_token(token):
    try:
        jwt.decode(token, SETTINGS.WORLD_EDITOR_SECRET, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True
