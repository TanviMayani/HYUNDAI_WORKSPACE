"""
Module providing database operations related to user sign-up.

This module includes functions to add business, groups, members, and keys to the database.
It also defines the SignUpQuery class for querying sign-up-related data.

Functions:
- add_business_to_db: Adds a new business to the database.
- add_groups_to_db: Adds default admin group with permissions to the database.
- add_member_data_to_db: Adds a new member to the database.
- add_keys_to_db: Adds API keys for a member to the database.

Classes:
- SignUpQuery: Provides methods for querying sign-up-related data, such as checking for existing emails.
"""

from sqlalchemy.orm import sessionmaker
from app.models import Members,Keys

def add_member_data_to_db(db,first_name,last_name,email,encrypted_password):
    """
    Adds a new member entry to the database.

    Parameters:
    - db: Database session.
    - first_name (str): First name of the member.
    - last_name (str): Last name of the member.
    - country_code (str): Country code of the member's phone number.
    - mobile_number (str): Mobile number of the member.
    - email (str): Email address of the member.
    - encrypted_password (str): Encrypted password for the member.
    - groups: The group object to associate the member with.

    Returns:
    - Members: The newly created member object.
    """
    member = Members(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=encrypted_password,
        email_verified=False,
        is_enabled=True,
        is_deleted=False,
        is_default=True,
        login_count=0,
    )
    db.add(member)
    db.commit()
    return member

def add_keys_to_db(db,member_id,api_key):
    """
    Adds a new API key entry to the database for a specific member.

    Parameters:
    - db: Database session.
    - member_id (int): ID of the member to associate the key with.
    - api_key (str): The API key to be added.

    Returns:
    - Keys: The newly created key object.
    """
    new_key = Keys(
        member_id=member_id,
        key=api_key,
        is_active=True,
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key


class SignUpQuery:
    """
    Query class for sign-up related operations.
    """

    @staticmethod
    def get_member_by_email_id(email: str, db_session: sessionmaker) -> bool:
        """
        Retrieve a member from the database by email.
        Parameters:
        - email (str): Email address of the member to retrieve.
        - db_session (sessionmaker): Database session to execute the query.
        Returns:
        - bool: True if the email exists, False otherwise.
        """
        db = db_session()
        email_exists = db.query(Members.id).filter(Members.email == email).first()
        return email_exists
