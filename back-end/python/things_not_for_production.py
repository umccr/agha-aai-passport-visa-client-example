from utils.logging import LOG
from aiohttp import web
from aiohttp_session import get_session, new_session
from session import session_key_login_id_token, session_key_login_access_token
#
# We have chosen to collect here a variety of routes/helpers etc. that are
# included in this codebase purely because it is a demonstration that is
# meant to *only* run on localhost for development.
#
# So wherever the code does something that is not production quality
# there will be a reference to a function/variable in this file.
#
# If this file is still needed and yet you are deploying for real - you
# have done something very wrong.
#

dev_routes = web.RouteTableDef()


@dev_routes.post(r"/api/login-bypass-{num:\d}")
async def login_bypass(request: web.Request):
    """
    Skip a login OIDC flow and just pretend they logged in as a fixed test user.
    Obviously needs to be removed for any production system.
    """
    LOG.debug("POST /api/login-bypass wildcard received")

    session = await new_session(request)
    session[session_key_login_id_token()] = "AMadeUpNotARealIdTokenForTestUser" + request.match_info["num"]
    session[session_key_login_access_token()] = "AMadeUpNotARealAccessTokenForTestUser" + request.match_info["num"]

    # note this needs to be 303 (not 307 or 308) to get the correct POST becomes GET behaviour
    response = web.HTTPSeeOther("/")

    if request.match_info["num"] == "1":
        response.set_cookie("logged_in_sub", "urn:example:test1")
        response.set_cookie("logged_in_name", "Test User 1")
        response.set_cookie("logged_in_email", "test1@example.com")
    elif request.match_info["num"] == "2":
        response.set_cookie("logged_in_sub", "urn:example:test2")
        response.set_cookie("logged_in_name", "Test User 2")
        response.set_cookie("logged_in_email", "test2@example.com")
    else:
        response = web.HTTPSeeOther("/not-authorized/no-login-oidc-configured")

    return response


@dev_routes.get("/api/logged-in-user-info")
async def logged_in_user_info(request: web.Request):
    """
    Dump from our encrypted session state all the information that is known to the
    backend (i.e. tokens etc.). This would obviously not be exposed to the frontend
    at all in a production system.
    """
    LOG.debug("GET /api/logged-in-user-info received")

    session = await get_session(request)

    LOG.debug(session)

    # we need to do some dict() construction to get the session compatible with the JSON encoder
    return web.json_response(dict(session.items()))


def drs_host_whitelist(hostname: str):
    return True


def htsget_host_whitelist(hostname: str):
    return True


def fhir_host_whitelist(hostname: str):
    return True


def beacon_host_whitelist(hostname: str):
    return True
