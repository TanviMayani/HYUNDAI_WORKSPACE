import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import get_db
from app.helpers import authenticate, format_response, handle_error
from app.logging_utils import logger
from app.models import Members

class ProfileRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/v1/hiib", tags=["Profile Router"])
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("/v1/idp/members/profile", tags=["Profile Router"])(self.get_profile)
        self.router.patch("/v1/idp/members/profile", tags=["Profile Router"])(self.update_profile)

    async def get_profile(
        self,
        db: Session = Depends(get_db),
        user_id: str = Depends(authenticate)
    ):
        try:
            member = db.query(Members).filter(Members.id == int(user_id)).first()
            if not member:
                handle_error("user_not_found", "get_profile", "User profile not found")

            data = {
                "id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "full_name": f"{member.first_name} {member.last_name}",
                "email": member.email,
                "login_count": member.login_count or 0,
                "last_login": member.last_login.isoformat() if member.last_login else None,
                "profile_photo": member.profile_photo,
                "created_at": str(member.created_at) if member.created_at else None
            }
            logger(level="INFO", status_code=200, message=f"Profile retrieved for user {user_id}", endpoint="get_profile")
            return format_response(detail_type="success", msg="record_fetched", data=data)
        except HTTPException:
            raise
        except Exception as e:
            logger(level="ERROR", status_code=500, message=f"Error fetching profile: {e}", endpoint="get_profile")
            handle_error("exception_error", "get_profile", f"Error fetching profile: {e}")

    async def update_profile(
        self,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        user_id: str = Depends(authenticate)
    ):
        try:
            member = db.query(Members).filter(Members.id == int(user_id)).first()
            if not member:
                handle_error("user_not_found", "update_profile", "User profile not found")

            if first_name:
                member.first_name = first_name
            if last_name:
                member.last_name = last_name

            if file:
                profile_dir = os.path.join(os.getcwd(), "uploads", "profiles")
                os.makedirs(profile_dir, exist_ok=True)
                
                ext = file.filename.split(".")[-1] if "." in file.filename else "png"
                filename = f"user_{user_id}_avatar.{ext}"
                file_path = os.path.join(profile_dir, filename)

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
                photo_url = f"{server_base_url}/uploads/profiles/{filename}"
                member.profile_photo = photo_url

            db.add(member)
            db.commit()
            db.refresh(member)

            data = {
                "id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "full_name": f"{member.first_name} {member.last_name}",
                "email": member.email,
                "login_count": member.login_count or 0,
                "last_login": member.last_login.isoformat() if member.last_login else None,
                "profile_photo": member.profile_photo
            }
            logger(level="INFO", status_code=200, message=f"Profile updated for user {user_id}", endpoint="update_profile")
            return format_response(detail_type="success", msg="record_updated", data=data)
        except HTTPException:
            raise
        except Exception as e:
            logger(level="ERROR", status_code=500, message=f"Error updating profile: {e}", endpoint="update_profile")
            handle_error("exception_error", "update_profile", f"Error updating profile: {e}")
