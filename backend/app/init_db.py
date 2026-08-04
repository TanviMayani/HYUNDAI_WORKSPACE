from sqlalchemy.orm import sessionmaker
from .models import Base, Methods, MethodName
from .config import engine
import hashlib
from uuid import uuid4  # Import uuid4


def generate_module_id(module_name):
    """Generate a unique module ID using module name."""
    str2hash = "Binary Semantics Limited" + module_name
    result = hashlib.md5(str2hash.encode())
    return result.hexdigest()


def insert_default_methods(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.no_autoflush:
            default_methods = [
                {"display_name": "LLM Extraction", "internal_name": MethodName.llm},
                {"display_name": "MSME Captcha Extraction", "internal_name": MethodName.msme_extract_captcha},

            ]

            for method in default_methods:
                exists = session.query(Methods).filter_by(internal_name=method["internal_name"]).first()
                if not exists:
                    new_method = Methods(
                        display_name=method["display_name"], 
                        internal_name=method["internal_name"]
                    )
                    session.add(new_method)
        
        session.commit()

    except Exception as error:
        session.rollback()
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    insert_default_methods(engine)
