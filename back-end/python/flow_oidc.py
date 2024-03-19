import aiohttp.web
import aiohttp_session
import jwt
from aiohttp import web

from oidc_helper import (
    CALLBACK_ROUTE,
    get_oidc_redirect_uri_from_env,
    get_client_id,
    get_issuer, )
from server_constants import key_oidc_client, key_oidc_server_jwks
from utils.logging import LOG
from session import session_key_login_id_token, session_key_login_access_token

oidc_routes = web.RouteTableDef()

# for demonstration system we do not have to worry about actually managing
# the state of multiple flows
OIDC_STATE = "ABCD"




@oidc_routes.post("/login")
async def auth(request: aiohttp.web.Request):
    """Initiate OIDC flow."""
    LOG.debug("POST /login received.")

    authorize_url = request.app[key_oidc_client].get_authorize_url(
        scope="openid email profile",
        state=OIDC_STATE,
        redirect_uri=get_oidc_redirect_uri_from_env(),
    )

    LOG.info("Starting OIDC flow to URL '%s'", authorize_url)

    return web.HTTPTemporaryRedirect(authorize_url)


@oidc_routes.get(CALLBACK_ROUTE)
async def callback(request: aiohttp.web.Request):
    """
    Get the code from an OIDC flow (via callback) and then exchange that for a token.
    """
    LOG.debug("GET /callback received.")

    code = request.query["code"]
    state = request.query["state"]

    if state != OIDC_STATE:
        raise Exception("State mismatch on login flow")

    oidc_client = request.app[key_oidc_client]

    LOG.debug("OIDC client client id '%s'", oidc_client.client_id)
    LOG.debug("OIDC client access token url '%s'", oidc_client.access_token_url)

    # do a token exchange of the code for real tokens
    _, tokens = await oidc_client.get_access_token(
        code,
        redirect_uri=get_oidc_redirect_uri_from_env()
    )

    LOG.debug(tokens)

    # we downloaded the login server JWKS on service start
    oidc_server_jwks = request.app[key_oidc_server_jwks]

    # OIDC/ID TOKEN JWT handling
    # importantly we cannot trust some of the fields here (i.e. alg)
    id_token = tokens["id_token"]

    header = jwt.get_unverified_header(id_token)

    if header["alg"] not in ["RS256", "RS384", "RS512"]:
        raise Exception("Algorithm from login OIDC flow was not one from our white list")

    alg = header["alg"]
    kid = header["kid"]

    decoded = jwt.decode(
        id_token,
        oidc_server_jwks[kid].key,
        algorithms=[alg],
        audience=get_client_id(),
        issuer=get_issuer(),
        options={},
    )

    LOG.debug(decoded)

    # now store the new JWT in our encrypted session state
    session = await aiohttp_session.new_session(request)
    session[session_key_login_id_token()] = tokens["id_token"]
    session[session_key_login_access_token()] = tokens["access_token"]

    # response sending them back to the work page but also set some useful cookies for the frontend
    response = web.HTTPTemporaryRedirect("/work")
    response.set_cookie("logged_in_name", decoded["name"])
    response.set_cookie("logged_in_email", decoded["email"])
    response.set_cookie("logged_in_sub", decoded["sub"])

    return response
