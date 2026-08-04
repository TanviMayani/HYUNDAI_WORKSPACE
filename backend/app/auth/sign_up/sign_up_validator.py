from pydantic import BaseModel, EmailStr, validator
from app.validators import (
    check_first_name,
    check_last_name,
    check_password,
)
from app.helpers import handle_error

class UserData(BaseModel):
    """
    Pydantic model representing user data for sign-up.
    Attributes:
    - first_name (str): First name of the user.
    - last_name (str): Last name of the user.
    - country_code (str): Country code for the user's mobile number.
    - mobile_number (str): Mobile number of the user without the country code.
    - business_name (str): Business name of the user.
    - email (EmailStr): Email address of the user.
    - password (str): Password chosen by the user.
    - confirm_password (str): Confirmation of the password.
    """

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

    _check_first_name = validator("first_name")(check_first_name)
    _check_last_name = validator("last_name")(check_last_name)
    _check_password = validator("password")(check_password)

    @validator("email")
    def business_email_validator(cls, v):
        """
        Validator for validating business email domains.
        Parameters:
        - v (str): Email address to be validated.
        Returns:
        - str: Validated email address.
        Raises:
        - ValueError: If the email domain is not allowed.
        """
        business_email_domains = [
            "binarysemantics.com",
            "hiib.in"
        ]  
        email_domain = v.split("@")[-1]
        if email_domain not in business_email_domains:
            handle_error("email_error", "business_email_validator")
        return v
