"""
API_KEY_ROUTER class for handling API key management routes and operations.

Classes:
    API_KEY_ROUTER: Handles API routes for creating and retrieving API keys.

Functions:
    __init__: Initializes the API_KEY_ROUTER with necessary configurations.
    add_routes: Sets up the API routes for the router.
    create_api_key: Generates a new API key for an authenticated user.
    get_api_key: Retrieves the active API key for an authenticated user.
"""

# Standard library imports
import os
import uuid

# Third-party imports
from jose import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

# Local application imports
from app.models import Keys
from app.config import get_db
from app.token import JWTBearer
from app.logging_utils import logger
from .api_key_access import deactivate_previous_keys
from app.helpers import format_response, exception_format_response, load_error_details

error_details = load_error_details("error_details.json")

class API_KEY_ROUTER:
    """
    Handles API routes for creating and retrieving API keys.

    Attributes:
        router (APIRouter): FastAPI router for API key routes.
    """

    def __init__(self):
        """
        Initializes the API_KEY_ROUTER with necessary configurations.
        """
        self.router = APIRouter(prefix="/v1/hiib", tags=["api_key_router"])

    def add_routes(self):
        """
        Sets up the API routes for the router.
        """
        self.router.add_api_route(
            "/create_api_key", endpoint=self.create_api_key, methods=["POST"]
        )
        self.router.add_api_route(
            "/get_api_key", endpoint=self.get_api_key, methods=["GET"]
        )

    async def create_api_key(
        self, db: Session = Depends(get_db), dependencies=Depends(JWTBearer())
    ):
        """
        Generates a new API key for an authenticated user.

        Args:
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            dict: Success response with the generated API key.

        Raises:
            HTTPException: If an error occurs during key creation.
        """
        try:
            logger(
                level="INFO",
                status_code=200,
                message="Attempting to create API key",
                endpoint="/create_api_key",
            )

            token = dependencies
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), os.getenv("ALGORITHM"))
            user_id = payload["sub"]
            api_key = str(uuid.uuid4().hex)[:20]

            data = {"api_key": api_key}
            deactivate_previous_keys(db, user_id)

            new_key = Keys(member_id=user_id, key=api_key, is_active=True)
            db.add(new_key)
            db.commit()

            success_response = format_response(
                detail_type="success",
                data=data,
                msg="api_key_generated",
            )

            traceback_id = success_response["detail"][0]["traceback_id"]

            logger(
                level="INFO",
                status_code=200,
                message=f"API key generated successfully for user id {user_id}",
                endpoint="/create_api_key",
                traceback_id=traceback_id,
            )

            return success_response

        except jwt.ExpiredSignatureError:
            self._handle_jwt_error("expire_error", "/create_api_key")
        except jwt.JWTError:
            self._handle_jwt_error("decode_error", "/create_api_key")
        except Exception as e:
            self._handle_generic_error(e, "/create_api_key")

    async def get_api_key(
        self, db: Session = Depends(get_db), dependencies=Depends(JWTBearer())
    ):
        """
        Retrieves the active API key for an authenticated user.

        Args:
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            dict: Success response with the active API key.

        Raises:
            HTTPException: If no active API key is found or another error occurs.
        """
        try:
            token = dependencies
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), os.getenv("ALGORITHM"))
            user_id = payload["sub"]

            logger(
                level="INFO",
                status_code=200,
                message=f"Attempting to get API key for user ID {user_id}",
                endpoint="/get_api_key",
            )

            active_key = (
                db.query(Keys)
                .filter(Keys.member_id == user_id, Keys.is_active == True)
                .first()
            )

            if active_key:
                data = {"api_key": active_key.key}
                success_response = format_response(
                    detail_type="success", data=data, msg="api_key_fetched"
                )

                traceback_id = success_response["detail"][0]["traceback_id"]

                logger(
                    level="INFO",
                    status_code=200,
                    message=f"API key fetched successfully for user ID {user_id}",
                    endpoint="/get_api_key",
                    traceback_id=traceback_id,
                )

                return success_response

            else:
                self._handle_key_not_found("invalid_api", "/get_api_key")

        except jwt.ExpiredSignatureError:
            self._handle_jwt_error("expire_error", "/get_api_key")
        except jwt.JWTError:
            self._handle_jwt_error("decode_error", "/get_api_key")
        except Exception as e:
            self._handle_generic_error(e, "/get_api_key")

    def _handle_jwt_error(self, error_type: str, endpoint: str):
        """
        Handles JWT-related errors and raises an HTTPException.

        Args:
            error_type (str): Type of JWT error.
            endpoint (str): API endpoint where the error occurred.
        """
        response = exception_format_response(
            detail_type=error_details[error_type]["detail_type"],
            msg=error_details[error_type]["msg"],
            reason=error_details[error_type]["reason"],
        )

        traceback_id = response["traceback_id"]

        logger(
            level="ERROR",
            status_code=401,
            message=f"{error_type} {response}",
            endpoint=endpoint,
            traceback_id=traceback_id,
        )

        raise HTTPException(
            status_code=error_details[error_type]["status_code"], detail=[response]
        )

    def _handle_key_not_found(self, error_type: str, endpoint: str):
        """
        Handles cases where no active API key is found and raises an HTTPException.

        Args:
            error_type (str): Type of error.
            endpoint (str): API endpoint where the error occurred.
        """
        response = exception_format_response(
            detail_type=error_details[error_type]["detail_type"],
            msg=error_details[error_type]["msg"],
            reason=error_details[error_type]["reason"],
        )

        traceback_id = response["traceback_id"]

        logger(
            level="ERROR",
            status_code=404,
            message=f"{error_type} {response}",
            endpoint=endpoint,
            traceback_id=traceback_id,
        )

        raise HTTPException(
            status_code=error_details[error_type]["status_code"], detail=[response]
        )

    def _handle_generic_error(self, exception: Exception, endpoint: str):
        """
        Handles generic exceptions and raises an HTTPException.

        Args:
            exception (Exception): The exception that occurred.
            endpoint (str): API endpoint where the error occurred.
        """
        error_type = "exception_error"
        error_msg = f"An error occurred: {str(exception)}"
        error_details[error_type]["reason"].format(error_msg=error_msg)

        response = exception_format_response(
            detail_type=error_details[error_type]["detail_type"],
            msg=error_details[error_type]["msg"],
            reason=error_msg,
        )

        traceback_id = response["traceback_id"]

        logger(
            level="CRITICAL",
            status_code=500,
            message=f"{error_type} {response}",
            endpoint=endpoint,
            traceback_id=traceback_id,
        )
        return response
