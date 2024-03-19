from utils.logging import LOG
from aiohttp import web, FormData
from aiohttp_session import get_session, new_session
from server_constants import key_oidc_client, key_brokers
from session import session_key_passport_scoped_access_token, session_key_passport_token


STATIC_STATE = "SOMESTATE"

#
# A passport broker flow from the perspective of a client
#

passport_routes = web.RouteTableDef()


@passport_routes.post(r"/login-broker-{num:\d}")
async def login_broker_n(request: web.Request):
    """Initiate OIDC flow."""
    LOG.debug("POST /login received.")

    num = int(request.match_info["num"])

    broker_tuple = request.app[key_brokers][num - 1]

    authorize_url = broker_tuple[0].get_authorize_url(
        scope="openid ga4gh",
        state=STATIC_STATE,
        redirect_uri=f"http://localhost:3000/callback-broker-{num}",
    )

    LOG.info("Starting broker flow to URL '%s'", authorize_url)

    return web.HTTPSeeOther(authorize_url)


@passport_routes.post(r"/logout-broker-{num:\d}")
async def logout_broker_n(request: web.Request):
    """Delete all related data from the given broker"""
    LOG.debug("POST /logout received.")

    num = int(request.match_info["num"])

    broker_tuple = request.app[key_brokers][num - 1]

    # our session is where we securely store all our tokens
    session = await get_session(request)

    if session_key_passport_scoped_access_token(num) in session:
        del session[session_key_passport_scoped_access_token(num)]

    if session_key_passport_token(num) in session:
        del session[session_key_passport_token(num)]

    return web.json_response({"ok": True})


@passport_routes.get(r"/callback-broker-{num:\d}")
async def callback_broker_n(request: web.Request):
    """
    Get the code from an OIDC flow (via callback) and then exchange that for a passport-scoped access token.
    """
    LOG.debug("GET /callback received.")

    num = int(request.match_info["num"])

    broker_tuple = request.app[key_brokers][num - 1]

    code = request.query["code"]
    state = request.query["state"]

    # TODO could implement proper state
    if state != STATIC_STATE:
        raise Exception("State mismatch on broker flow")

    LOG.debug("Broker client client id '%s'", broker_tuple[0].client_id)
    LOG.debug("Broker client access token url '%s'", broker_tuple[0].access_token_url)

    # do a code exchange for OIDC tokens
    _, tokens = await broker_tuple[0].get_access_token(
        code,
        redirect_uri=f"http://localhost:3000/callback-broker-{num}"
    )

    # we need to store some of the tokens in our encrypted session state
    session = await get_session(request)

    session[session_key_passport_scoped_access_token(num)] = tokens["access_token"]

    # send them back to the main work page
    response = web.HTTPTemporaryRedirect("/work")

    return response


@passport_routes.post(r"/exchange-broker-{num:\d}")
async def exchange_broker_n(request: web.Request):
    """
    Do an exchange of our passport scoped access token for a real passport
    """
    LOG.debug("POST /exchange received.")

    try:
        num = int(request.match_info["num"])

        broker_tuple = request.app[key_brokers][num - 1]

        # our session is where we securely store all our tokens
        session = await get_session(request)

        psat = session[session_key_passport_scoped_access_token(num)]

        exchange_form_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "requested_token_type": "urn:ga4gh:params:oauth:token-type:passport",
            "subject_token": psat,
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            # "actor_token": "",
            # "actor_token_type": "urn:ga4gh:params:",
            # TODO: allow the frontend to change these
            # "scope": "blah",
            # "resource": ["https://drs1.example.com/dataset1", "https://drs2.example.com/dataset1"],
            # "audience": ["https://who1.com", "https://who2.com"]
        }

        # now do an exchange to get a GA4GH passport
        data = await broker_tuple[0]._request(
            "POST",
            broker_tuple[0].access_token_url,
            raise_for_status=False,
            auth=(broker_tuple[0].client_id, broker_tuple[0].client_secret),
            data=exchange_form_data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            }
        )

        print(data)

        session[session_key_passport_token(num)] = data["access_token"]
    except Exception as e:
        print(e)
        return web.json_response({
            "error": str(e)
        }, status=400)

    return web.json_response({"ok": True})
