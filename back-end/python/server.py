import os
import sys

from aiohttp import web

from flow_oidc import oidc_routes
from flow_passport import passport_routes
from flow_logout import logout_routes
from http_server_helper import sanitize_path
from oidc_helper import (
    get_login_flow_client_from_env,
    create_oauth2_client,
)
from server_constants import key_oidc_client, key_oidc_server_jwks, key_static_folder, key_brokers
from session import setup_session
from things_not_for_production import dev_routes
from utils.logging import LOG

routes = web.RouteTableDef()


@routes.get("/{tail:.*}", name="index")
async def index(request):
    """
    Catch-all file handler endpoint. This technique is useful for React/VueJs
    front ends which use their own URL routing on the front end. As long as their
    route names do not clash with actual files on disk - both can work together
    seamlessly.

    Returns the content of a file if it exists, else the contents of index.html
    """
    LOG.debug("Catch all file handler endpoint.")

    # the static folder is configured to tell us the absolute path of the front end files
    # we want to serve the files up in a way that is suitable for React/Vuejs etc
    static_folder = request.app[key_static_folder]

    if request.path != "/" and request.path != "/index.html":
        # check if the file (say /assets/myfile.jpg) actually exists on the disk underneath
        # our static folder root
        file_path = sanitize_path(
            request.app[key_static_folder], request.path[1:]
        )

        # if it exists then serve it up
        if file_path:
            # because we are serving up vitejs built react that uses asset checksums - we can be
            # very aggressive on the caching of these - even in dev
            return web.FileResponse(
                file_path,
                headers={
                    "Cache-Control": "public, max-age=31536000",
                },
            )

    # otherwise - to best support routing in React/Vuejs - we serve up the index.html
    # for all other requests

    # because our index.html does not have an asset checksum - we make sure it is not cached
    return web.FileResponse(
        os.path.join(static_folder, "index.html"),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def init_app(static_folder: str):
    """Initialise the web server."""
    LOG.info("Initialising web server.")

    app = web.Application(middlewares=[])

    # we will store client state in an encrypted session managed by the web server
    setup_session(app)

    # these all go before regular "routes" as we need to come first before the wildcard route
    app.router.add_routes(dev_routes)
    app.router.add_routes(logout_routes)
    app.router.add_routes(passport_routes)

    # NOTE: whilst this code works, it requires an OIDC secret and custom setup so is temporarily
    # disabled - will re-enable with more instruactions at some point
    # app.router.add_routes(oidc_routes)

    # our regular routes serve up the HTML and base APIs
    app.router.add_routes(routes)

    # pass through to the rest of the app where the front-end files live
    app[key_static_folder] = static_folder

    # configured OIDC client
    #oc, oc_jwks = await get_login_flow_client_from_env()

    #app[key_oidc_client] = oc
    #app[key_oidc_server_jwks] = oc_jwks

    broker1_client, broker1_jwks = await create_oauth2_client("https://broker-usa.aai.dev.umccr.org")
    broker2_client, broker2_jwks = await create_oauth2_client("https://broker-europe.aai.dev.umccr.org")
    broker3_client, broker3_jwks = await create_oauth2_client("https://broker-australia.aai.dev.umccr.org")

    app[key_brokers] = [
        [broker1_client, broker1_jwks],
        [broker2_client, broker2_jwks],
        [broker3_client, broker3_jwks]
    ]

    return app


def main():
    """
    The main process that runs a web server
    """
    LOG.setLevel("DEBUG")

    LOG.info("Starting server.")
    LOG.info(f"Location of main Python file is {__file__}")

    # NOTE: this technique is specifically for dev scenarios in this demonstration
    #       code - production setup would be different

    # this is where our actual server python file as an absolute path
    # we will then use this path to try to locate our "frontend" files
    root_py_path = os.path.dirname(os.path.abspath(__file__))

    # find the absolute path of where the built UI static files should be
    abs_static_folder = os.path.realpath(
        os.path.join(root_py_path, "..", "..", "front-end", "build")
    )

    missing_index_error_message = (f"Needs to be able to find and read the 'index.html'"
                                   f" file in folder '{abs_static_folder}' - have you built the"
                                   f" front-end? (see the top level README.md for build instructions)")

    if not os.path.isdir(abs_static_folder):
        LOG.error(missing_index_error_message)
        sys.exit(1)

    if not os.path.isfile(os.path.join(abs_static_folder, "index.html")):
        LOG.error(missing_index_error_message)
        sys.exit(1)

    web.run_app(
        init_app(abs_static_folder),
        host="localhost",
        port=3000,
        shutdown_timeout=0,
    )


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        LOG.error("Requires python 3.6 or higher")
        sys.exit(1)

    main()
