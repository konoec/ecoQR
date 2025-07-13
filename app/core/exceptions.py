from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import traceback
from typing import Union


class EcoRewardsException(Exception):
    """Base exception for EcoRewards application"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(EcoRewardsException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(EcoRewardsException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403)


class NotFoundError(EcoRewardsException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ValidationError(EcoRewardsException):
    """Validation related errors"""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 422)


class BusinessLogicError(EcoRewardsException):
    """Business logic related errors"""
    
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, 400)


class ExternalServiceError(EcoRewardsException):
    """External service related errors"""
    
    def __init__(self, message: str = "External service error"):
        super().__init__(message, 502)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the FastAPI app"""
    
    @app.exception_handler(EcoRewardsException)
    async def ecorewards_exception_handler(request: Request, exc: EcoRewardsException):
        logger.error(f"EcoRewards Exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "type": exc.__class__.__name__,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "type": "HTTPException",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation failed",
                "type": "ValidationError",
                "details": exc.errors(),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Database operation failed",
                "type": "DatabaseError",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected Error: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "type": "InternalServerError",
                "path": request.url.path
            }
        )
