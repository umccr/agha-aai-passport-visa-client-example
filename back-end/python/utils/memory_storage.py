import json
import uuid
from typing import Any, Callable, Optional

from aiohttp import web
from aiohttp_session import AbstractStorage, Session

# have taken the Redis storage engine
# https://github.com/aio-libs/aiohttp-session/blob/master/aiohttp_session/redis_storage.py
# and just downgraded it to store data in memory
# this is absolutely utterly *not* suitable as a session manager for any real environment
# (all session state is lost on restart of the server)
state: dict[str, Any] = {}


class MemoryStorage(AbstractStorage):
    """Memory storage"""

    def __init__(
        self,
        *,
        cookie_name: str = "AIOHTTP_SESSION",
        domain: Optional[str] = None,
        max_age: Optional[int] = None,
        path: str = "/",
        secure: Optional[bool] = None,
        httponly: bool = True,
        samesite: Optional[str] = None,
        key_factory: Callable[[], str] = lambda: uuid.uuid4().hex,
        encoder: Callable[[object], str] = json.dumps,
        decoder: Callable[[str], Any] = json.loads,
    ) -> None:
        super().__init__(
            cookie_name=cookie_name,
            domain=domain,
            max_age=max_age,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
            encoder=encoder,
            decoder=decoder,
        )
        self._key_factory = key_factory

    async def load_session(self, request: web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            key = str(cookie)

            if key not in state:
                return Session(None, data=None, new=True, max_age=self.max_age)

            data_str = state[key]
            try:
                data = self._decoder(data_str)
            except ValueError:
                data = None
            return Session(key, data=data, new=False, max_age=self.max_age)

    async def save_session(
        self, request: web.Request, response: web.StreamResponse, session: Session
    ) -> None:
        key = session.identity
        if key is None:
            key = self._key_factory()
            self.save_cookie(response, key, max_age=session.max_age)
        else:
            if session.empty:
                self.save_cookie(response, "", max_age=session.max_age)
            else:
                key = str(key)
                self.save_cookie(response, key, max_age=session.max_age)

        data_str = self._encoder(self._get_session_data(session))
        state[key] = data_str

        # if we added in TTL we would use ex=session.max_age,
