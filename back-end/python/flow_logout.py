import aiohttp.web
import aiohttp_session
from aiohttp import web


logout_routes = web.RouteTableDef()

@logout_routes.post("/logout")
async def auth(request: aiohttp.web.Request):
    """
    Destroy the session/cookies of any login OIDC flow that exists
    """

    session = await aiohttp_session.get_session(request)
    session.invalidate()

    response = web.HTTPSeeOther("/")
    response.del_cookie("logged_in_sub")
    response.del_cookie("logged_in_name")
    response.del_cookie("logged_in_email")

    return response
