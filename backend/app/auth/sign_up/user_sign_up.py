"""
Module handling the user sign-up process, including routing and database operations.

Classes:
- SignUpRouter: Manages the sign-up API endpoint and related operations.

Functions:
- sign_up: Handles the sign-up logic, including data validation, business, group, member, and key creation.
"""

# Standard library imports
import uuid

# Third-party imports
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status

# Local application imports
from app.logging_utils import logger
from .sign_up_validator import UserData
from app.auth.utils import PasswordManager
from app.config import SessionLocal, get_db
from app.helpers import format_response, exception_format_response, load_error_details
from .sign_up_access import SignUpQuery, add_keys_to_db, add_member_data_to_db

error_details = load_error_details("error_details.json")


class SignUpRouter:
    """
    Manages the sign-up API endpoint.

    Methods:
    - __init__: Initializes the router with the signup endpoint.
    - sign_up: Handles the sign-up logic and interacts with the database.
    """

    def __init__(self):
        """Initialize SignUpRouter."""
        self.router = APIRouter(prefix="/v1/hiib", tags=["sign_up_router"])
        self.router.post("/signup", status_code=status.HTTP_201_CREATED)(self.sign_up)

    async def sign_up(self, payload: UserData, db: Session = Depends(get_db)):
        """
        Handles the user sign-up process.

        Parameters:
        - payload (UserData): The incoming request data containing user details.
        - db (Session): The database session dependency.

        Returns:
        - dict: Success response on successful sign-up.

        Raises:
        - HTTPException: If any validation fails or an error occurs during processing.
        """
        try:
            first_name = payload.first_name
            last_name = payload.last_name
            email = payload.email
            password = payload.password
            confirm_password = payload.confirm_password

            logger(level='INFO', status_code=200,message=str(payload),endpoint='/signup')


            if password != confirm_password:
                error_type = "sign_up_password_mismatch_error"
                response = exception_format_response(
                    detail_type=error_details[error_type]["detail_type"],
                    msg=error_details[error_type]["msg"],
                    reason=error_details[error_type]["reason"],
                )
                traceback_id = response["traceback_id"]
                logger(level='ERROR',status_code=400,message=str(error_type)+str(response),endpoint='/signup',traceback_id=traceback_id)
                raise HTTPException(
                    status_code=error_details[error_type]["status_code"],
                    detail=[response],
                )

            email = email.lower()
            existing_user = SignUpQuery.get_member_by_email_id(email, SessionLocal)

            if existing_user:
                error_type = "sign_up_mismatch_error"
                response = exception_format_response(
                    detail_type=error_details[error_type]["detail_type"],
                    msg=error_details[error_type]["msg"],
                    reason=error_details[error_type]["reason"],
                )
                traceback_id = response["traceback_id"]
                logger(level='ERROR',status_code=409,message=str(error_type)+str(response),endpoint='/signup',traceback_id=traceback_id)
                raise HTTPException(
                    status_code=error_details[error_type]["status_code"],
                    detail=[response],
                )
            password_manager = PasswordManager()
            encrypted_password = password_manager.get_hashed_password(password)

            member = add_member_data_to_db(db,first_name,last_name,email,encrypted_password)
            logger(level='INFO', status_code=200, message="Added member data into the database", endpoint='/signup')
            
            api_key = str(uuid.uuid4().hex)[:20]
            new_key = add_keys_to_db(db,member.id,api_key)
            logger(level='INFO', status_code=200, message=f"Added Keys data into the database: {new_key}", endpoint='/signup')

            success_response = format_response(
                detail_type="success", msg="user_signed_up"
            )
            traceback_id = success_response['detail'][0]['traceback_id']
            logger(level='INFO', status_code=200, message='User signed up successfully' + " " + str(email), endpoint='/signup', traceback_id=traceback_id)

            return success_response
        except HTTPException:
            raise

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"An error occurred: {str(e)}"
            error_details[error_type]["reason"].format(error_msg=error_msg)
            response = exception_format_response(
                detail_type=error_details[error_type]["detail_type"],
                msg=error_details[error_type]["msg"],
                reason=error_msg,
            )
            traceback_id = response["traceback_id"]
            logger(level='CRITICAL',status_code=500,message=str(error_type)+str(response),endpoint='/signup',traceback_id=traceback_id)

            raise HTTPException(
                status_code=error_details[error_type]["status_code"], detail=[response]
            )
        
sign_up_router = SignUpRouter()
