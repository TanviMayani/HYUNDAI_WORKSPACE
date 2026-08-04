import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

def create_db_engine():
    try:
        database_url = os.getenv("DATABASE_URL")
        print(database_url)
        if database_url is None:
            raise ValueError("DATABASE_URL environment variable is not set")

        engine = create_engine(
            database_url,
            pool_size=30,         
            max_overflow=50,      
            pool_timeout=60        
        )
        print("Connection established successfully to PostgreSQL")
        return engine
    except Exception as error:
        print("Error while connecting to PostgreSQL", error)
        return None

engine = create_db_engine()

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
