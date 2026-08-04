"""
Module defining the PasswordManager class for password hashing and verification.
Attributes:
- CryptContext: Class for password hashing and verification.
Classes:
- PasswordManager: Utility class for password hashing and verification using the Argon2 algorithm.
"""

from passlib.context import CryptContext


class PasswordManager:
    """
    Utility class for password hashing and verification using the Argon2 algorithm.
    Methods:
    - __init__: Initializes the PasswordManager with the Argon2 password hashing context.
    - get_hashed_password: Hashes a given password using the Argon2 algorithm.
    - verify_password: Verifies a given password against a hashed password.
    """

    def __init__(self):
        """
        Initializes the PasswordManager with the Argon2 password hashing context.
        """
        self.password_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def get_hashed_password(self, password: str) -> str:
        """
        Hashes the given password using Argon2 algorithm.
        Parameters:
        - password (str): The password to be hashed.
        Returns:
        - str: The hashed password.
        """
        return self.password_context.hash(password)

    def verify_password(self, password: str, hashed_pass: str) -> bool:
        """
        Verifies the given password against the hashed password.
        Parameters:
        - password (str): The password to be verified.
        - hashed_pass (str): The hashed password to compare against.
        Returns:
        - bool: True if the password matches the hashed password, False otherwise.
        """
        return self.password_context.verify(password, hashed_pass)
