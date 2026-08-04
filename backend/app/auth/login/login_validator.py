"""
This module defines Pydantic models for data validation in user login requests.
Classes:
- UserData: Pydantic BaseModel for validating user login data.
Usage:
- Import the UserData class from this module and use it for validating user login data.
"""

from pydantic import BaseModel, EmailStr


class UserData(BaseModel):
    """
    Pydantic BaseModel for validating user login data.
    Attributes:
    - email (EmailStr): Email address of the user.
    - password (str): Password of the user.
    Usage:
    - Create an instance of UserData with email and password.
    """

    email: EmailStr
    password: str
