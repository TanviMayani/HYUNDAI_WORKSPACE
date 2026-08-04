"""
This module defines the `JobDocumentService` class, which provides methods for managing jobs and documents in the database.

Key Features:
- Authenticate users with jobs and documents.
- Add, retrieve, and delete jobs and documents.
- Validate and generate job names and document IDs.
- Manage job and document processing status.
- Fetch associated methods and job details from the database.

Components:
- `JobDocumentService`: A service class with static methods for database interactions related to jobs and documents.

Dependencies:
- SQLAlchemy for database ORM.
- FastAPI for exception handling.
- Logging utilities for detailed error and info logging.
- Python standard libraries for utilities like UUID and hashlib.

Error Handling:
- SQLAlchemy exceptions are caught and logged.
- Custom HTTP exceptions for database errors.

Usage:
- Call static methods of `JobDocumentService` to perform job and document-related database operations.
"""

# Standard Library Imports
import os
import uuid
import httpx
import hashlib
import tempfile
from datetime import datetime
from typing import List, Union, Optional

# Third-Party Imports
import json
import requests
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, func
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import SQLAlchemyError

# Local Application Imports
from app.models import Documents, Jobs, Methods
from app.logging_utils import logger
from dotenv import load_dotenv
from app.helpers import format_response
from fastapi.encoders import jsonable_encoder

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CLIENTSECRET = os.getenv("CLIENTSECRET")
CLIENTID = os.getenv("CLIENTID")
IP = os.getenv("IP")

HEADERS = {
    "ClientSecret": CLIENTSECRET,
    "ClientId": CLIENTID,
    "IP": IP,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class JobDocumentService:
    """
    Service class for managing jobs and documents in the database.
    """

    @staticmethod
    def get_user_id_from_job(db: Session, job_id: str) -> Optional[str]:
        """
        Retrieve user ID from job data.

        Args:
            db (Session): Database session.
            job_id (str): Job ID.

        Returns:
            Optional[str]: User ID if found, else None.
        """
        user_id = db.query(Jobs.created_by).filter(Jobs.id == job_id).first()
        return user_id[0] if user_id else None

    @staticmethod
    def authenticate_user_with_document(db: Session, user_id: str, document_id: str) -> bool:
        """
        Authenticate user with a document.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            document_id (str): Document ID.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        job_id = db.query(Documents.job_id).filter(Documents.document_id == document_id).first()
        if not job_id:
            return False
        document_user_id = JobDocumentService.get_user_id_from_job(db, job_id[0])
        return str(document_user_id) == str(user_id)

    @staticmethod
    def authenticate_user_with_job(db: Session, user_id: str, job_id: str) -> bool:
        """
        Authenticate user with a job.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            job_id (str): Job ID.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        try:
            job = db.query(Jobs).filter_by(id=job_id).first()
            if job and str(job.created_by) == str(user_id):
                return True
            return False
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error occurred while authenticating user with job: {e}", endpoint='authenticate_user_with_job')
            return False
     
       
    @staticmethod
    def send_to_webhook(job_data: dict):
        """Send job data to a webhook asynchronously."""
        if not WEBHOOK_URL:
            logger(level="ERROR", status_code=500,
                message="WEBHOOK_URL is not configured",
                endpoint="send_to_webhook")
            return

        with httpx.Client(timeout=30.0, verify=False) as client:
            try:
                logger(level="INFO", status_code=200,
                    message=f"Sending webhook request to: {WEBHOOK_URL}",
                    endpoint="send_to_webhook")
                json_data = jsonable_encoder(job_data)
                response = client.post(WEBHOOK_URL, json=json_data, headers=HEADERS)
                
                if response.status_code == 200:
                    logger(level="INFO", status_code=200,
                        message="Successfully sent data to webhook",
                        endpoint="send_to_webhook")
                else:
                    logger(level="ERROR", status_code=response.status_code,
                        message=f"Failed to send data to webhook: {response.text}",
                        endpoint="send_to_webhook")
                    
            except httpx.TimeoutException:
                logger(level="ERROR", status_code=504,
                    message="Webhook request timed out",
                    endpoint="send_to_webhook")
            except (httpx.ConnectError, httpx.RequestError) as req_err:
                logger(level="ERROR", status_code=502,
                    message=f"Webhook connection error: {str(req_err)}",
                    endpoint="send_to_webhook")
            except Exception as e:
                logger(level="ERROR", status_code=500,
                    message=f"Exception while sending data to webhook: {str(e)}",
                    endpoint="send_to_webhook")
                   
    @staticmethod
    def process_job_completion(job_id: str, db: Session):
        """Check if the job is completed and send the data to the webhook."""
        from .job_helpers import document_processing_service
        from .jobs_validator import JobsResponse, JobsResponseList
        try:
            job_data = JobDocumentService.get_job_by_id(job_id, db)
            logger(level="INFO", status_code=200, 
                message=f"Processing job completion for job_id: {job_id}", 
                endpoint="process_job_completion")

            if not job_data:
                logger(level="ERROR", status_code=404, 
                    message=f"Job data not found for job_id: {job_id}", 
                    endpoint="process_job_completion")
                return

            job_data['job_id'] = job_data.pop('id')
            for source in job_data.get('source', []):
                source['document_id'] = source.pop('id')
                documents = JobDocumentService.get_document_by_id(source['document_id'], db)

                if not documents:
                    logger(level="ERROR", status_code=404, 
                        message=f"Documents not found for document_id: {source['document_id']}", 
                        endpoint="process_job_completion")
                    continue

                updated_results = []
                for document in documents:
                    if document.result:
                        try:
                            document_results = json.loads(document.result)
                            if isinstance(document_results, dict):
                                document_results = [document_results]

                            for result in document_results:
                                if isinstance(result, dict):
                                    result['page_number'] = document.page_number
                                    updated_results.append(result)
                        except json.JSONDecodeError as e:
                            logger(level="ERROR", status_code=500,
                                message=f"Failed to parse document result JSON: {str(e)}",
                                endpoint="process_job_completion")

                source['result'] = updated_results

            job_item = JobsResponse(**job_data)
            job_item.created_at = document_processing_service.convert_to_ist(job_item.created_at)
            job_item.updated_at = document_processing_service.convert_to_ist(job_item.updated_at)
            job_item.job_start_time = document_processing_service.convert_to_ist(job_item.job_start_time)
            job_item.job_end_time = document_processing_service.convert_to_ist(job_item.job_end_time)

            logger(level="INFO", status_code=200,
                message=f"Sending webhook data for job_id: {job_id}",
                endpoint="process_job_completion")
            
            response_data = JobsResponseList(data_list=[job_item])
            final_response_data = format_response(detail_type="success", msg="record_fetched", data=response_data.data_list)
            JobDocumentService.send_to_webhook(final_response_data)
            
            logger(level="INFO", status_code=200,
                message=f"Successfully processed job completion for job_id: {job_id}",
                endpoint="process_job_completion")

        except Exception as e:
            logger(level="ERROR", status_code=500,
                message=f"Error processing job completion: {str(e)}",
                endpoint="process_job_completion")
            raise
            
    @staticmethod
    def validate_job_name(value: str) -> str:
        """
        Validate the job name.

        Args:
            value (str): Job name to validate.

        Returns:
            str: Validated job name.

        Raises:
            ValueError: If job name exceeds 30 characters.
        """
        if len(value) > 30:
            raise ValueError("Job name must be less than 30 characters")
        return value

    @staticmethod
    def delete_job_by_id(db, job_id):
        """
        Delete a job and its associated documents by job ID.

        Args:
            db (Session): Database session.
            job_id (str): Job ID to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        try:
            job = db.query(Jobs).filter(Jobs.id == job_id).one()
            documents = db.query(Documents).filter(Documents.job_id == job_id).all()

            for document in documents:
                db.delete(document)

            db.delete(job)
            db.commit()
            logger(level='CRITICAL', status_code=500, message=f"Job and associated documents deleted successfully for job_id: {job_id}", endpoint='delete_job_by_id')
            return True

        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error while delete job id: {e}", endpoint='delete_job_by_id')
            db.rollback()
            return False
    
    @staticmethod
    def add_data_to_job_table(
        id: str,
        db: Session,
        process: str,
        source: str,
        status: str,
        job_name: str,
        method: str,
        created_by: str
    ) -> bool:
        """
        Add data to the Jobs table.

        Args:
            id (str): Job ID.
            db (Session): Database session.
            process (str): Job process type.
            source (str): Job source.
            status (str): Job status.
            job_name (str): Job name.
            method (str): Method used for the job.
            created_by (str): User ID who created the job.

        Returns:
            bool: True if added successfully, False otherwise.
        """
        current_datetime = datetime.now()
        jobs = Jobs(
            id=id,
            process=process,
            source=source,
            status=status,
            job_name=job_name,
            method=method,
            job_start_time=current_datetime,
            created_by=created_by
        )

        try:
            db.add(jobs)
            db.commit()
            db.refresh(jobs)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger(level='CRITICAL', status_code=500, message=f"Error adding job to the database: {e}", endpoint='add_data_to_job_table')
            return False

    @staticmethod
    def model_to_dict(model) -> dict:
        """
        Convert a SQLAlchemy model instance into a dictionary.

        Args:
            model: SQLAlchemy model instance.

        Returns:
            dict: Dictionary representation of the model.
        """
        return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}

    @staticmethod
    def get_document_by_id(document_id: str, db_session: Session) -> List[Documents]:
        """
        Retrieve document data by document ID from the database.

        Args:
            document_id (str): Document ID.
            db_session (Session): Database session.

        Returns:
            List[Documents]: List of documents matching the ID.
        """
        return (
            db_session.query(Documents)
            .filter(Documents.document_id == document_id)
            .order_by(Documents.page_number.asc())
            .all()
        )

    @staticmethod
    def check_all_documents_processed(job_id: str, expected_count: int, db: Session) -> bool:
        """
        Check if all documents associated with a job ID have been processed.

        Args:
            job_id (str): Job ID.
            expected_count (int): Expected number of documents.
            db (Session): Database session.

        Returns:
            bool: True if all documents are processed, False otherwise.
        """
        distinct_document_count = db.query(func.count(func.distinct(Documents.document_id))).filter(
            Documents.job_id == job_id).scalar()
        logger(level="INFO", status_code=200, message=f"distinct_document_count: {distinct_document_count}, expected_count: {expected_count}", endpoint="check_all_documents_processed")
        return distinct_document_count == expected_count

    @staticmethod
    def get_all_documents(job_id: str, db_session: Session) -> List[dict]:
        """
        Retrieve all documents associated with a specific job from the database.

        Args:
            job_id (str): The job ID.
            db_session (Session): Database session.

        Returns:
            List[dict]: List of documents associated with the specified job.
        """
        documents = db_session.query(Documents).filter(Documents.job_id == job_id).all()
        document_ids = list(set(doc.document_id for doc in documents))

        unique_documents = []
        if document_ids:
            unique_docs_query = db_session.query(Documents).filter(
                Documents.document_id.in_(document_ids)).distinct(Documents.document_id).all()

            for doc in unique_docs_query:
                doc_dict = JobDocumentService.model_to_dict(doc)
                doc_dict['job_id'] = str(doc_dict['job_id'])
                unique_documents.append(doc_dict)

        return unique_documents

    @staticmethod
    def get_job_by_id(job_id: str, db_session: Session) -> Optional[dict]:
        from .job_helpers import document_processing_service
        """
        Retrieve job data by job ID from the database, including document details.

        Args:
            job_id (str): The job ID.
            db_session (Session): Database session.

        Returns:
            Optional[dict]: Dictionary containing job details and associated documents, or None if not found.
        """
        job = db_session.query(Jobs).filter(Jobs.id == job_id).first()

        if not job:
            return None

        job_dict = JobDocumentService.model_to_dict(job)
        job_dict['id'] = str(job_dict['id'])

        documents = db_session.query(
            Documents.document_id,
            Documents.document_url,
            Documents.document_name,
            Documents.pages,
            Documents.file_size
        ).filter(Documents.job_id == job.id).distinct(Documents.document_id).all()

        job_dict['source'] = [
            {
                'id': str(document.document_id),
                'url': document_processing_service.generate_presigned_url(document.document_url),
                'name': document.document_name,
                'total_page': document.pages,
                'size': document.file_size
            }
            for document in documents
        ]

        return job_dict

    @staticmethod
    def get_job_by_user_id(user_id: Union[str, int], db_session: Session) -> List[dict]:
        from .job_helpers import document_processing_service
        """
        Retrieve all jobs created by a specific user from the database.

        Args:
            user_id (Union[str, int]): The user ID.
            db_session (Session): Database session.

        Returns:
            List[dict]: List of jobs created by the user, including associated documents.
        """
        user_id = str(user_id)

        def fetch_job_documents(job_id: int) -> List[dict]:
            documents = db_session.query(
                Documents.document_id,
                Documents.document_url,
                Documents.document_name,
                Documents.pages,
                Documents.file_size
            ).filter(Documents.job_id == job_id).distinct(Documents.document_id).all()

            return [
                {
                    'id': str(document.document_id),
                    'url': document_processing_service.generate_presigned_url(document.document_url),
                    'name': document.document_name,
                    'total_page': document.pages,
                    'size': document.file_size
                }
                for document in documents
            ]

        def process_job(job) -> dict:
            job_dict = JobDocumentService.model_to_dict(job)
            job_dict['id'] = str(job_dict['id'])
            job_dict['source'] = fetch_job_documents(job.id)
            return job_dict

        jobs = db_session.query(Jobs).filter(
            cast(Jobs.created_by, String) == user_id
        ).order_by(Jobs.created_at.desc()).all()

        return [process_job(job) for job in jobs]

    @staticmethod
    def filter_jobs_by_date_from_db(db_session: Session, user_id: str, start_date: str = None, end_date: str = None) -> list:
        try:
            query = db_session.query(Jobs).filter(cast(Jobs.created_by, String) == user_id)
            if start_date:
                query = query.filter(cast(Jobs.created_at, String) >= f"{start_date} 00:00:00")
            if end_date:
                query = query.filter(cast(Jobs.created_at, String) <= f"{end_date} 23:59:59")

            jobs = query.order_by(Jobs.created_at.desc()).all()

            def fetch_job_documents(job_id: str) -> list:
                from .job_helpers import document_processing_service
                documents = db_session.query(Documents).filter(Documents.job_id == job_id).all()
                return [
                    {
                        'id': str(doc.document_id),
                        'url': document_processing_service.generate_presigned_url(doc.document_url),
                        'name': doc.document_name,
                        'total_page': doc.pages,
                        'size': doc.file_size
                    }
                    for doc in documents
                ]

            def process_job(job) -> dict:
                job_dict = JobDocumentService.model_to_dict(job)
                job_dict['id'] = str(job_dict['id'])
                job_dict['source'] = fetch_job_documents(job.id)
                return job_dict

            return [process_job(job) for job in jobs]
        except Exception as e:
            logger(level="ERROR", status_code=500, message=f"Failed to filter jobs by date: {e}", endpoint="filter_jobs_by_date_from_db")
            return []

    @staticmethod
    def add_document_to_db(
        db: Session,
        job_id: str,
        file_name: str,
        file_size: int,
        document_type: str,
        status: str,
        num_pages: int,
        page_number: int,
        json_string: str,
        document_id: str,
        source_url: str,
        file_url: str,
        input_tokens: int = None,
        output_tokens: int = None
    ) -> bool:
        """
        Add a document entry to the database.

        Args:
            db (Session): Database session.
            job_id (str): Associated job ID.
            file_name (str): Document file name.
            file_size (int): Size of the document in bytes.
            document_type (str): Type of the document (e.g., PDF, JPEG).
            status (str): Processing status of the document.
            num_pages (int): Number of pages in the document.
            page_number (int): Current page number being processed.
            json_string (str): Extracted JSON string from the document.
            document_id (str): Unique document ID.
            source_url (str): Source URL of the document.
            file_url (str): File URL for the document.
            input_tokens (int, optional): Number of input tokens used during processing.
            output_tokens (int, optional): Number of output tokens used during processing.

        Returns:
            bool: True if added successfully, False otherwise.
        """

        document = Documents(
            id=uuid.uuid4(),
            job_id=job_id,
            document_name=file_name,
            file_size=file_size,
            type=document_type,
            status=status,
            pages=num_pages,
            page_number=page_number,
            result=json_string,
            document_id=document_id,
            document_url=source_url,
            file_url=file_url,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        try:
            db.add(document)
            db.commit()
            db.refresh(document)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger(level='CRITICAL', status_code=500, message=f"Error adding document to the database: {e}", endpoint='add_document_to_db')
            return False

    @staticmethod
    def add_document_to_db_pending(
        db: Session,
        job_id: str,
        file_name: str,
        file_size: int,
        document_type: str,
        status: str,
        num_pages: int,
        document_id: str,
        source_url: str,
        file_url: str
    ) -> bool:
        """
        Add a pending document entry to the database.

        Args:
            db (Session): Database session.
            job_id (str): Associated job ID.
            file_name (str): Document file name.
            file_size (int): Size of the document in bytes.
            document_type (str): Type of the document (e.g., PDF, JPEG).
            status (str): Initial processing status.
            num_pages (int): Number of pages in the document.
            document_id (str): Unique document ID.
            source_url (str): Source URL of the document.
            file_url (str): File URL for the document.

        Returns:
            bool: True if added successfully, False otherwise.
        """
        document = Documents(
            id=uuid.uuid4(),
            job_id=job_id,
            document_name=file_name,
            file_size=file_size,
            type=document_type,
            status=status,
            pages=num_pages,
            document_id=document_id,
            document_url=source_url,
            file_url=file_url
        )

        try:
            db.add(document)
            db.commit()
            db.refresh(document)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger(level='CRITICAL', status_code=500, message=f"Error adding pending document to the database: {e}", endpoint='add_document_to_db_pending')
            return False

    @staticmethod
    def generate_document_id(job_id: str) -> Optional[str]:
        """
        Generate a unique document ID based on the job ID.

        Args:
            job_id (str): Job ID.

        Returns:
            Optional[str]: Generated document ID, or None if an error occurs.
        """
        try:
            str2hash = "Binary Semantics Limited" + str(job_id) + str(uuid.uuid4())
            document_id = hashlib.md5(str2hash.encode()).hexdigest()
            return document_id
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error generating document ID: {e}", endpoint='generate_document_id')
            return None

    @staticmethod
    def get_method_list_from_db(db: Session) -> List[dict]:
        """
        Fetch a list of methods from the database.

        Args:
            db (Session): Database session.

        Returns:
            List[dict]: List of method dictionaries containing method IDs and display names.
        """
        try:
            method_list = db.query(Methods.id, Methods.display_name).all()
            return [{"id": str(method.id), "display_name": method.display_name} for method in method_list]
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error fetching method list: {e}", endpoint='get_method_list_from_db')
            return []

    @staticmethod
    def get_method_from_id(db: Session, method_id: str) -> tuple:
        """
        Fetch method details by ID.

        Args:
            db (Session): Database session.
            method_id (str): Method ID to fetch.

        Returns:
            tuple: Tuple containing method display name and internal name, or (None, None) if not found or invalid.
        """
        import uuid
        try:
            # Validate UUID format to prevent database syntax errors
            uuid.UUID(method_id)
        except ValueError:
            logger(level='WARNING', status_code=400, message=f"Invalid UUID format for method_id: {method_id}", endpoint='get_method_from_id')
            return None, None

        try:
            method = db.query(Methods).filter(Methods.id == method_id).first()
            if method:
                return method.display_name, method.internal_name
            return None, None
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error fetching method by ID: {e}", endpoint='get_method_from_id')
            return None, None

    @staticmethod
    def url_to_image_path(presigned_url: str) -> str:
        """
        Download an S3 object using its bucket name and key, and return the local file path.

        Parameters:
        - presigned_url (str): The presigned URL for the file in S3.

        Returns:
        - str: The local file path where the file is saved.
        """
        if not presigned_url:
            return presigned_url

        clean_url = presigned_url.replace("file:///", "")
        if os.path.exists(clean_url):
            return clean_url

        if "uploads/" in presigned_url.replace("\\", "/"):
            clean_rel = presigned_url.replace("\\", "/")
            rel = clean_rel[clean_rel.find("uploads/"):]
            local_p = os.path.join(os.getcwd(), rel)
            if os.path.exists(local_p):
                return local_p

        if not (presigned_url.startswith("https://") or presigned_url.startswith("http://")):
            raise ValueError("The provided URL must start with 'https://' or 'http://' or be a valid local file path")

        temp_folder_name = uuid.uuid4().hex
        temp_folder_path = os.path.join(tempfile.gettempdir(), temp_folder_name)
        os.makedirs(temp_folder_path)

        temp_file_path = os.path.join(
            temp_folder_path, f"{uuid.uuid4().hex}.png"
        )

        try:
            response = requests.get(presigned_url)
            response.raise_for_status()  
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            # if not os.path.isfile(temp_file_path):
            #     raise RuntimeError("File was not saved properly.")
            return temp_file_path
        except Exception as e:
            # os.remove(temp_file_path)
            raise RuntimeError(f"Failed to download file from presigned URL: {e}")
