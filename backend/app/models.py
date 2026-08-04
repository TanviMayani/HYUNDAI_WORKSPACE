from sqlalchemy import Column, DateTime, Integer, String, Boolean, TEXT, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TEXT, UUID
from enum import Enum as PythonEnum
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class TimeStamp_at(Base):
    __abstract__ = True

    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat() + "Z", onupdate=lambda: datetime.utcnow().isoformat() + "Z")
    
class MethodName(PythonEnum):
    llm = "llm"
    msme_extract_captcha = "msme_extract_captcha"

class Status(PythonEnum):
    Failed = "Failed"
    In_Process = "In_Process"
    Completed = "Completed" 

class Jobs(TimeStamp_at, Base):
    __tablename__ = 'tbl_jobs'
    id = Column(UUID(as_uuid=True), primary_key=True)
    status  =Column(Enum(Status, name="status"), nullable=False)
    job_start_time =  Column(DateTime(timezone=True))
    job_end_time = Column(DateTime(timezone=True))
    process  = Column(String)
    job_name = Column(String)
    method = Column(String)
    source  = Column(String)
    created_by  = Column(String)

class Documents(TimeStamp_at, Base):
    __tablename__ = 'tbl_documents'
    id  = Column(UUID(as_uuid=True), primary_key=True)
    job_id = Column(UUID(as_uuid=True))
    document_name    = Column(String)
    status  =Column(Enum(Status, name="status"), nullable=False)
    type    = Column(String)
    result  = Column(TEXT)
    pages   = Column(Integer)
    file_size  = Column(Integer)
    page_number = Column(Integer)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    document_id = Column(String)
    document_url = Column(String)
    file_url = Column(String)
 
class Methods(Base):
    __tablename__ = 'tbl_methods'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False) 
    display_name = Column(String)  
    internal_name = Column(Enum(MethodName, name="method_name_enum"))  

class Members(TimeStamp_at, Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50),  nullable=False)
    last_name = Column(String(50),  nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    profile_photo = Column(String(200))
    email_verified = Column(Boolean)
    token = Column(String(500))
    login_count = Column(Integer())
    is_default = Column(Boolean,default=False)
    is_enabled = Column(Boolean)
    is_deleted = Column(Boolean,default=False)
    last_login= Column(DateTime(timezone=True))

class Keys(TimeStamp_at, Base):
    __tablename__ = "keys"
    member_id = Column(Integer)
    key = Column(String(450), primary_key=True)
    is_active = Column(Boolean)