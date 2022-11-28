import os

from fastapi import FastAPI, Request
# from fastapi.responses import RedirectResponse
import uvicorn

# from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
# from authlib.integrations.starlette_client import OAuth, OAuthError



if __name__ == '__main__':
    uvicorn.run("fast_fhirstorm:app",
                host='127.0.0.1',
                port=8080,
                log_level="info",
                reload=True)
#                # ssl_keyfile="../ssl/localhost.key",
#                # ssl_certfile="../ssl/localhost.crt")
    print("running")