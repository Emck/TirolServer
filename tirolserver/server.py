import sys

import gunicorn.app.wsgiapp
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tirolserver.routers.api import router_api

# create app
app: FastAPI = FastAPI(title="Tirol Server")
"""FastAPI instance"""


# include routes
app.include_router(router_api)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
	"""http exception handler by fastapi.
	:param request: original request
	:param exc: class HTTPException
	:return: json format
	"""
	return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


"""main function"""


def main():
	"""main function"""
	sys.argv = ["gunicorn", "tirolserver.server:app", "-c", "tirolserver/config.py"]
	gunicorn.app.wsgiapp.run()


if __name__ == "__main__":
	main()
