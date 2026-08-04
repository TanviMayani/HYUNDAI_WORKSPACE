"""
This module provides the login functionality for user authentication.

Key Features:
- Endpoint: POST /v1/idp/login for user login.
- Validates user credentials and issues JWT tokens.
- Logs login attempts and errors.

Components:
- LoginRouter: Manages the login endpoint.
- login: Handles authentication and token generation.

Dependencies:
- FastAPI for request handling.
- SQLAlchemy for database operations.
- Local modules for config, authentication, and logging utilities.

Error Handling:
- Custom error responses with HTTPException.
- Detailed logging for all significant events.

Usage:
- Initialize `LoginRouter` to add the login route to the FastAPI app.
"""

# Standard library imports
from datetime import datetime

# Third-party imports
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

# Local application imports
from app.config import get_db
from .login_access import logInQuery
from app.logging_utils import logger
from .login_validator import UserData
from app.auth.utils import PasswordManager
from app.helpers import format_response, create_access_token, exception_format_response, load_error_details


error_details = load_error_details('error_details.json')

class LoginRouter:
    """
    Class to handle user login endpoint.
    """

    def __init__(self):
        """Initialize LoginRouter."""
        self.router = APIRouter(prefix="/v1/hiib", tags=["login_router"])
        self.router.post("/login")(self.login)

    async def login(self, data: UserData, db: Session = Depends(get_db)):
        """
        Endpoint to handle user login.
        Parameters:
        - data (UserData): User data including email and password.
        - db (Session, optional): Database session. Defaults to Depends(get_db).
        Returns:
        - JSON Response: Success or error message with appropriate status codes.
        Raises:
        - HTTPException: If the user does not exist, the password is incorrect,
        or any unexpected error occurs during the process.
        """
        try:
            email = data.email.lower()
            password = data.password
            logger(level='INFO', status_code=200,message='login Initiating email'+" "+email,endpoint='/login')

            user = logInQuery.get_member_by_email_id(email, db)

            if user is None:
                error_type = 'login_not_found_error'
                response = exception_format_response(
                    detail_type=error_details[error_type]["detail_type"],
                    msg=error_details[error_type]["msg"],
                    reason=error_details[error_type]["reason"],
                )
                traceback_id = response["traceback_id"]
                logger(level='ERROR',status_code=404,message=str(error_type)+str(response),endpoint='/login',traceback_id=traceback_id)
                raise HTTPException(
                    status_code=error_details[error_type]["status_code"], detail=[response]
                )

            password_manager = PasswordManager()
            if not password_manager.verify_password(password, user.password):
                error_type = 'login_unauthorised_error'
                response = exception_format_response(
                    detail_type=error_details[error_type]["detail_type"],
                    msg=error_details[error_type]["msg"],
                    reason=error_details[error_type]["reason"],
                )
                traceback_id = response["traceback_id"]
                logger(level='ERROR',status_code=401,message=str(error_type)+str(response),endpoint='/login',traceback_id=traceback_id)
                raise HTTPException(
                    status_code=error_details[error_type]["status_code"], detail=[response]
                )

            current_datetime = datetime.now()

            token = create_access_token(user.id)

            user.token = token
            user.last_login = current_datetime
            user.login_count = (user.login_count or 0) + 1
            db.add(user)
            db.commit()
            db.refresh(user)

            token_response = {"token": token}
            success_response = format_response(
                detail_type="success",
                data=token_response,
                msg="user_logged_in",
            )
            traceback_id = success_response['detail'][0]['traceback_id']
            logger(level='INFO', status_code=200, message='User signed up successfully' + " " + str(email), endpoint='/signup', traceback_id=traceback_id)

            return success_response
        except HTTPException:
            # Re-raise HTTPException to maintain consistent handling
            raise

        except Exception as e:
            # Rollback changes in case of error
            db.rollback()
            # Raise HTTPException with status code 500 (Internal Server Error)
            error_type = 'exception_error'
            error_msg = f"An error occurred: {str(e)}"
            error_details[error_type]["reason"].format(error_msg=error_msg)
            response = exception_format_response(
                detail_type=error_details[error_type]["detail_type"], msg=error_details[error_type]["msg"], reason=error_msg
            )
            traceback_id = response["traceback_id"]
            logger(level='CRITICAL',status_code=500,message=str(error_type)+str(response),endpoint='/login',traceback_id=traceback_id)
            raise HTTPException(
                status_code=error_details[error_type]["status_code"], detail=[response]
            )


# Create an instance of LoginRouter
login_router = LoginRouter()
