import aiohttp_session
from aiohttp.abc import Application
from utils.memory_storage import MemoryStorage


def setup_session(app: Application):
    aiohttp_session.setup(app, MemoryStorage())


def session_key_login_id_token():
    return "Login Id Token"


def session_key_login_access_token():
    return "Login Access Token"


def session_key_passport_scoped_access_token(num: int):
    return f"Broker {num} Passport-Scoped Access Token"


def session_key_passport_token(num: int):
    return f"Broker {num} Passport"
