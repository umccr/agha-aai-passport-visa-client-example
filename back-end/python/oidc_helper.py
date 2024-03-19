import os
from typing import Optional

import aiohttp
from aioauth_client import OAuth2Client
from jwt import PyJWKSet

from utils.logging import LOG

CALLBACK_ROUTE = "/oidc/callback"

# AAI https://proxy.aai.lifescience-ri.eu/.well-known/openid-configuration

def get_deploy_url_from_env():
    #if not "DEPLOY_URL" in os.environ:
    #    raise Exception("Missing environment variables for DEPLOY_URL")

    return "http://localhost:3000"

    return os.environ["DEPLOY_URL"]


def get_oidc_redirect_uri_from_env():
    return get_deploy_url_from_env() + CALLBACK_ROUTE


def get_client_id():
    if "OIDC_CLIENT_ID" not in os.environ:
        raise Exception("Missing environment variables for OIDC_CLIENT_ID")

    return os.environ["OIDC_CLIENT_ID"]


def get_issuer():
    return os.environ["OIDC_LOGIN_SERVER"]


async def get_login_flow_client_from_env():
    """
    The login flow is the initial mechanism by which someone's authenticates to the
    server - and establishes an encrypted session.
    """
    login_server = get_issuer()
    authorization_endpoint = None
    token_endpoint = None

    if not "OIDC_CLIENT_SECRET" in os.environ:
        raise Exception("Missing environment variables for OIDC_CLIENT_SECRET")

    jwkset: Optional[PyJWKSet] = None

    async with aiohttp.ClientSession() as client:
        async with client.get(
            f"{login_server}/.well-known/openid-configuration"
        ) as response:
            if response.status == 200:
                oidc_config = await response.json()

                authorization_endpoint = oidc_config["authorization_endpoint"]
                token_endpoint = oidc_config["token_endpoint"]

        async with client.get(oidc_config["jwks_uri"]) as response:
            if response.status == 200:
                jwks = await response.json()

                jwkset = PyJWKSet.from_dict(jwks)

    if not authorization_endpoint:
        raise Exception("No login flow authorization URL discovered - this should be present in the '.well-known/openid-configuration' of the login server")

    if not token_endpoint:
        raise Exception("No login flow token exchange URL discovered - this should be present in the '.well-known/openid-configuration' of the login server")

    if not jwkset:
        raise Exception("No login flow JWKS was able to be discovered")

    return (
        OAuth2Client(
            client_id=get_client_id(),
            client_secret=os.environ["OIDC_CLIENT_SECRET"],
            base_url=login_server,
            authorize_url=authorization_endpoint,
            access_token_url=token_endpoint,
            logger=LOG,
        ),
        jwkset,
    )


async def create_oauth2_client(server):
    jwkset: Optional[PyJWKSet] = None

    async with aiohttp.ClientSession() as client:
        async with client.get(
            f"{server}/.well-known/openid-configuration"
        ) as response:
            if response.status == 200:
                oidc_config = await response.json()

                authorization_endpoint = oidc_config["authorization_endpoint"]
                token_endpoint = oidc_config["token_endpoint"]

        async with client.get(oidc_config["jwks_uri"]) as response:
            if response.status == 200:
                jwks = await response.json()

                jwkset = PyJWKSet.from_dict(jwks)

    if not authorization_endpoint:
        raise Exception("No broker flow authorization URL discovered - this should be present in the '.well-known/openid-configuration' of the login server")

    if not token_endpoint:
        raise Exception("No broker flow token exchange URL discovered - this should be present in the '.well-known/openid-configuration' of the login server")

    if not jwkset:
        raise Exception("No broker flow JWKS was able to be discovered")

    return (
        OAuth2Client(
            client_id="client",
            client_secret="secret",
            base_url=server,
            authorize_url=authorization_endpoint,
            access_token_url=token_endpoint,
            logger=LOG,
        ),
        jwkset,
    )
