from typing import Tuple, List

from aioauth_client import OAuth2Client
from aiohttp import web
from jwt import PyJWKSet

# keys for data/state we store inside the server requests
key_static_folder = web.AppKey("static_folder", str)


key_oidc_client = web.AppKey("oidc_client", OAuth2Client)
key_oidc_server_jwks = web.AppKey("oidc_server_jwks_key", PyJWKSet)

key_brokers = web.AppKey("brokers", List[Tuple[OAuth2Client, PyJWKSet]])
