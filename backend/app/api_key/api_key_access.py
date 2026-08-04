from sqlalchemy.orm import Session
from app.models import Keys

def deactivate_previous_keys(db: Session, user_id: int):
    """
    Deactivates all previous keys for the given user.
    """
    db.query(Keys).filter(Keys.member_id == user_id).update({"is_active": False})
