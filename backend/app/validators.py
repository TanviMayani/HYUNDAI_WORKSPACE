"""
This module provides functions for validating various fields commonly found in user profiles and business information.

Functions:
    - check_business_name: Validates a business name.
    - check_first_name: Validates a first name.
    - check_last_name: Validates a last name.
    - check_password: Validates a password based on specific criteria.
    - validate_confirm_password: Validates a confirm password field.
    - check_business_profile_name: Validates a business profile name.
    - check_business_address: Validates a business address.
    - check_gst: Validates a GST (Goods and Services Tax) number.

"""

import re
from app.helpers import handle_error

def check_first_name(cls, v):
    """
    Validates a first name.

    Args:
        cls: The class.
        v (str): The value to be validated.

    Raises:
        ValueError: If the length is not between 1 and 30 characters, or if it does not contain only alphabetic characters.

    Returns:
        str: The validated first name.
    """
    if not 1 <= len(v) <= 30:
        handle_error("name_length_error", "check_first_name")
    if not v.isalpha():
        handle_error("name_alphabet_error", "check_first_name")
    return v


def check_last_name(cls, v):
    """
    Validates a last name.

    Args:
        cls: The class.
        v (str): The value to be validated.

    Raises:
        ValueError: If the length is not between 1 and 30 characters, or if it does not contain only alphabetic characters.

    Returns:
        str: The validated last name.
    """
    if not 1 <= len(v) <= 30:
        handle_error("name_length_error", "check_last_name")
    if not v.isalpha():
        handle_error("name_alphabet_error", "check_last_name")
    return v


def check_password(cls, v):
    """
    Validates a password based on specific criteria.

    Args:
        cls: The class.
        v (str): The value to be validated.

    Raises:
        ValueError: If the password length is not between 8 and 20 characters,
                    or if it does not contain at least one uppercase letter,
                    one lowercase letter, one digit, and one special character.

    Returns:
        str: The validated password.
    """
    if not 8 <= len(v) <= 20:
        handle_error("password_length_error", "check_password")

    password_pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])"
    if not re.match(password_pattern, v):
        handle_error("password_complexity_error", "check_password")
    return v

def validate_confirm_password(value, values, **kwargs):
    """
    Validates a confirm password field.

    Args:
        value (str): The value to be validated.
        values (dict): A dictionary containing other values.
        **kwargs: Additional keyword arguments.

    Raises:
        ValueError: If the new password and confirm password do not match.

    Returns:
        str: The validated confirm password.
    """
    if "new_password" in values and value != values["new_password"]:
        handle_error("sign_up_password_mismatch_error","validate_confirm_password")
    return value