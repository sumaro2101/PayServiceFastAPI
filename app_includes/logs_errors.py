from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from http import HTTPStatus

from config.setup_logs.logging import logger
from api_v1.auth.exeptions import UnauthedExpeption, InvalidAlgorithm


def register_errors(app: FastAPI) -> None:
    """
    Крючек для логирования различных исключений
    """
    @app.exception_handler(InvalidAlgorithm)
    async def algorithm_error_handler(
        request: Request,
        exc: InvalidAlgorithm,
    ):
        """
        Логирование всех InvalidAlgorithm
        """
        logger.opt(exception=True).warning(exc)
        response = dict(
            status=False,
            error_code=exc.status_code,
            message=exc.detail,
        )
        return JSONResponse(response)

    @app.exception_handler(UnauthedExpeption)
    async def unauthed_error_handler(
        request: Request,
        exc: UnauthedExpeption,
    ):
        """
        Логирование всех ValiUnauthedExpeptiondationError
        """
        logger.opt(exception=True).warning(exc)
        response = dict(
            status=False,
            error_code=exc.status_code,
            message=exc.detail,
        )
        return JSONResponse(response)

    @app.exception_handler(HTTPException)
    async def http_error_handler(
        request: Request,
        exc: HTTPException,
    ):
        """
        Логирование всех HTTPException
        """
        logger.opt(exception=True).warning(exc)
        response = dict(
            status=False,
            error_code=exc.status_code,
            message=exc.detail,
        )
        return JSONResponse(response)

    @app.exception_handler(Exception)
    async def error_handler(
        request: Request,
        exc: Exception,
    ):
        """
        Логирование всех Exception
        """
        logger.exception(exc)
        response = dict(
            status=False,
            error_code=500,
            message=HTTPStatus(500).phrase,
        )
        return JSONResponse(response)

    @app.exception_handler(StarletteHTTPException)
    async def validation_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        """
        Логирование всех StarletteHTTPException
        """
        logger.opt(exception=True).warning(exc)
        response = dict(
            status=False,
            error_code=exc.status_code,
            message=exc.detail,
        )
        return JSONResponse(response)
