"""
This module defines a class for querying member data related to user login.
Classes:
- logInQuery: Class containing static methods for database queries related to user login.
Dependencies:
- src.models.Members: Model representing the Members table in the database.
"""
from app.models import Members
class logInQuery:
    """
    Class containing static methods for database queries related to user login.
    """
    @staticmethod
    def get_member_by_email_id(email: str, db_session) -> Members:
        """
        Retrieve a member from the database by email.
        Parameters:
        - email (str): Email address of the member to retrieve.
        - db_session: Database session.
        Returns:
        - Members: Member object if found, None otherwise.
        """
        email_exists = db_session.query(Members).filter(Members.email == email).first()
        return email_exists
