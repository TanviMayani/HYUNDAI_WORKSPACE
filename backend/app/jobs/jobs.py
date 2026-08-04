"""
JobRouter class for handling job-related API routes and operations.

Classes:
    JobRouter: Handles API routes and operations for job processing and document management.

Functions:
    __init__: Initializes the JobRouter with necessary configurations and dependencies.
    _setup_routes: Sets up the API routes for the router.
    create_job: Handles the creation of a new job for document processing.
    get_document: Retrieves a specific document by its document id.
    get_job: Retrieves a specific job by its job id.
    get_all_jobs: Retrieves all jobs associated with the authenticated user.
    get_all_jobs_pan: Retrieves all jobs associated with PAN documents for the authenticated user.
    get_all_jobs_aadhar: Retrieves all jobs associated with Aadhar documents for the authenticated user.
    get_all_jobs_cheque: Retrieves all jobs associated with cheque documents for the authenticated user.

"""

# Standard library imports
import os
import json
import uuid
import logging
from typing import List

# Third-party imports
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form, status, HTTPException, Body, Query
from pydantic import BaseModel
from fuzzywuzzy import fuzz

# Local application imports
from app.config import get_db
from app.logging_utils import logger
from app.models import Status, MethodName
from .jobs_access import JobDocumentService
from .job_helpers import document_processing_service
from .extract_captcha import msme_captcha_extraction
from app.helpers import format_response, load_error_details, authenticate, handle_error
from .jobs_validator import JobsResponseList, JobsResponse, DocumentsResponseList, DocumentsResponse, MethodResponse



class StringMatchRequest(BaseModel):
    strings: list[str]  # List of two strings to compare

class StringMatchResponse(BaseModel):
    strings: list[str]
    percentage: float

error_details = load_error_details("error_details.json")

class JobRouter:
    """
    Initialize the JobRouter with necessary configurations and dependencies.
    """
    def __init__(self):
        """
        Initialize the JobRouter with necessary configurations and dependencies.
        """
        self.router = APIRouter(prefix="/v1/hiib")

        load_dotenv()
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self._setup_routes()

    def _setup_routes(self):
        """
        Setup API routes for the router.
        """
        self.router.post("/job/invoice",tags=["Job Router"])(self.create_job_invoice)
        self.router.post("/job/captcha",tags=["Job Router"])(self.create_job_captcha)
        self.router.get("/job/filter/", tags=["Job Router"])(self.filter_jobs)
        self.router.get("/job/document/{document_id}", tags=["Job Router"])(self.get_document)
        self.router.get("/job/method/", tags=["Job Router"])(self.get_method_list)
        self.router.get("/job", tags=["Job Router"])(self.get_all_jobs)
        self.router.get("/job/{job_id}", tags=["Job Router"])(self.get_job)
        self.router.delete("/job/{job_id}", tags=["Job Router"])(self.delete_job)
        self.router.post("/stringmatch", tags=["Job Router"])(self.stringmatch)

    async def stringmatch(self,
                        string1: str = Body(...),
                        string2: str = Body(...)):
        """
        Compare two strings using advanced fuzzy logic and return the matching percentage.

        Args:
            string1 (str): The first input string.
            string2 (str): The second input string.

        Returns:
            JSONResponse: Response containing the two input strings and their matching percentage.
        """
        try:
            # Ensure the inputs are strings
            str1 = str(string1).strip().lower()
            str2 = str(string2).strip().lower()

            # Apply various fuzzy matching techniques
            ratio = fuzz.ratio(str1, str2)  # Basic ratio comparison
            partial_ratio = fuzz.partial_ratio(str1, str2)  # Partial matching
            token_sort_ratio = fuzz.token_sort_ratio(str1, str2)  # Token-based sorting and comparison
            token_set_ratio = fuzz.token_set_ratio(str1, str2)  # Token set-based comparison

            # Weighted average to calculate the final percentage
            matching_percentage = (
                0.4 * ratio + 0.3 * partial_ratio + 0.2 * token_sort_ratio + 0.1 * token_set_ratio
            )

            # Construct the response
            response_data = {
                "strings": [string1, string2],
                "percentage": f"{matching_percentage:.2f}",  # Format to 2 decimal places
              
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=format_response(detail_type="success", msg="Strings matched successfully", data=response_data),
            )

        except Exception as e:
            error_msg = f"An error occurred while performing string matching: {e}"
            handle_error("exception_error", "stringmatch", error_msg)



    async def create_job_invoice(self,
            background_tasks: BackgroundTasks,
            job_name: str = Form(...),   
            method_id: str = Form(...),
            file: UploadFile = File(...),
            db: Session = Depends(get_db),
            user_id: str = Depends(authenticate),
    ):
        """
        Create a new job for document processing.

        Args:
            background_tasks (BackgroundTasks): Background task manager.
            extract (str): JSON string specifying extraction options.
            files (List[UploadFile]): List of files to be processed.
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            JSONResponse: Response indicating success or failure of the job creation.
        """
        try:
            logger(level="INFO", status_code=200, message=f"Getting user id from the Authentication is : {user_id}",endpoint="create_job")
            job_id = uuid.uuid4()
            process = "single"

            method_display, method_internal = JobDocumentService.get_method_from_id(db, method_id)
            if not method_internal or not method_display:
                raise HTTPException(
                    status_code=400,
                    detail=[{
                        "type": "value_error",
                        "msg": "Invalid or non-existent method_id",
                        "loc": ["body", "method_id"]
                    }]
                )
            job_name = JobDocumentService.validate_job_name(job_name)
            logger(level="INFO", status_code=200, message=f"Getting method_display and  method_internal: {method_display} , {method_internal}",endpoint="create_job")
            total_files = 1
            num_pages = 1
            
            if process == "single":
                file_content = await file.read()
                saved_file_path = document_processing_service.save_uploaded_bytes(file.filename, file_content, str(job_id))
                file_name = os.path.basename(saved_file_path)
                file_size = len(file_content)
                document_name = file_name
                source_url = saved_file_path
                logger(level="INFO", status_code=200,message=f"Saved local file: {source_url}",endpoint="create_job")

                data_insert = JobDocumentService.add_data_to_job_table(str(job_id),db, process, source_url, Status.In_Process,job_name,method_display, user_id)
                if not data_insert:
                    error_type = "exception_error"
                    error_msg = f"Error while add document to database"
                    handle_error(error_type,"create_job_invoice",error_msg)
                    
                logger(level="INFO", status_code=200, message="Successfully added data to job table.",endpoint="create_job")
                document_type = document_processing_service.get_mimetypes(document_name)
                logger(level="INFO", status_code=200, message=f"Document type: {document_type}",endpoint="create_job")

                document_id = JobDocumentService.generate_document_id(job_id)
                logger(level="INFO", status_code=200, message=f"Generated Document ID: {document_id}",endpoint="create_job")

                if document_type == "application/pdf":
                    num_pages = document_processing_service.get_pdf_page_count(source_url, source_url)
                    logger(level="INFO", status_code=200,message=f"getting pdf pages is : {num_pages}",endpoint="create_job")

                background_tasks.add_task(
                    document_processing_service.extract_data,
                    file_name,
                    method_internal,
                    None,
                    document_type,
                    source_url,
                    "local",
                    document_name,
                    document_id,
                    job_id,
                    db,
                    total_files,
                    num_pages,
                    file_size,
                    file
                    )
                data = {"job_id": str(job_id)}
                response = format_response(detail_type="success", msg="instance_created", data=data)
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content=response,
                )

            elif process == "batch":
                folder_path = os.path.join(os.getcwd(), "uploads", str(job_id))
                os.makedirs(folder_path, exist_ok=True)
                data_insert = JobDocumentService.add_data_to_job_table(str(job_id),db,process,folder_path,Status.In_Process,job_name,method_display,user_id)
                if not data_insert:
                    error_type = "exception_error"
                    error_msg = f"Error while add document to database"
                    handle_error(error_type,"create_job_invoice",error_msg)
                logger(level="INFO", status_code=200, message="Successfully added data to job table.",endpoint="create_job")

                for file in files:
                    file_content = await file.read()
                    saved_file_path = document_processing_service.save_uploaded_bytes(file.filename, file_content, str(job_id))
                    source_url = saved_file_path
                    logger(level="INFO", status_code=200, message=f"Saved local file: {source_url}", endpoint="create_job")

                    document_name = os.path.basename(source_url)
                    logger(level="INFO", status_code=200,
                           message=f"File size: {str(file.size)}, Document name: {document_name}",
                           endpoint="create_job")

                    document_type = document_processing_service.get_mimetypes(document_name)
                    logger(level="INFO", status_code=200, message=f"Document type: {document_type}",endpoint="create_job")

                    document_id = JobDocumentService.generate_document_id(job_id)
                    logger(level="INFO", status_code=200, message=f"Generated Document ID: {document_id}",endpoint="create_job")

                    if document_type == "application/pdf":
                        num_pages = document_processing_service.get_pdf_page_count(source_url, source_url)
                        logger(level="INFO", status_code=200,message=f"getting pdf pages is : {num_pages}",endpoint="create_job")

                    background_tasks.add_task(
                        document_processing_service.extract_data,
                        file.filename,
                        method_internal,
                        None,
                        document_type,
                        source_url,
                        "local",
                        document_name,
                        document_id,
                        str(job_id),
                        db,
                        total_files,
                        num_pages,
                        file.size,
                        file
                    )
                data = {"_id": str(job_id)}
                return format_response(detail_type="success", msg="instance_created", data=data)

        except HTTPException:
            raise

        except Exception as e:
            error_msg = f"Facing error while create job: {e}"
            handle_error("exception_error","create_job_invoice",error_msg)

    async def create_job_captcha(self,
        background_tasks: BackgroundTasks,
        job_name: str = Form(...),
        method_id: str = Form(...),
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db),
        user_id: str = Depends(authenticate),
    ):
        """
        Create a new job for document processing.

        Args:
            background_tasks (BackgroundTasks): Background task manager.
            extract (str): JSON string specifying extraction options.
            files (List[UploadFile]): List of files to be processed.
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            JSONResponse: Response indicating success or failure of the job creation.
        """
        try:
            logger(level="INFO", status_code=200, message=f"Getting user id from the Authentication is create_job_captcha: {user_id}",endpoint="create_job_captcha")
            job_id = uuid.uuid4()
            process = "single"

            method_display, method_internal = JobDocumentService.get_method_from_id(db, method_id)
            if not method_internal or not method_display:
                raise HTTPException(
                    status_code=400,
                    detail=[{
                        "type": "value_error",
                        "msg": "Invalid or non-existent method_id",
                        "loc": ["body", "method_id"]
                    }]
                )
            job_name = JobDocumentService.validate_job_name(job_name)
            logger(level="INFO", status_code=200, message=f"Getting method_display and  method_internal : {method_display} , {method_internal}",endpoint="create_job_captcha")
            total_files = 1
            num_pages = 1
            
            file_content = await files[0].read()
            saved_file_path = document_processing_service.save_uploaded_bytes(files[0].filename, file_content, str(job_id))
            source_url = saved_file_path
            logger(level="INFO", status_code=200,message=f"Saved captcha file: {source_url}",endpoint="create_job_captcha")

            document_name = os.path.basename(source_url)
            logger(level="INFO", status_code=200,
                    message=f"File size: {files[0].size}, Document name: {document_name}",endpoint="create_job_captcha")

            data_insert = JobDocumentService.add_data_to_job_table(str(job_id),db, process, source_url, Status.In_Process,job_name,method_display, user_id)
            if not data_insert:
                error_type = "exception_error"
                error_msg = f"Error while add document to database"
                handle_error(error_type,"create_job_invoice",error_msg)
                
            logger(level="INFO", status_code=200, message="Successfully added data to job table.",endpoint="create_job_captcha")
            document_type = document_processing_service.get_mimetypes(document_name)
            logger(level="INFO", status_code=200, message=f"Document type: {document_type}",endpoint="create_job_captcha")

            document_id = JobDocumentService.generate_document_id(job_id)
            logger(level="INFO", status_code=200, message=f"Generated Document ID: {document_id}",endpoint="create_job_captcha")

            background_tasks.add_task(
                document_processing_service.extract_data,
                files[0].filename,
                method_internal,
                None,
                document_type,
                source_url,
                "local",
                document_name,
                document_id,
                job_id,
                db,
                total_files,
                num_pages,
                files[0].size,
                files[0]
            )
            extracted_captcha = ""
            if method_internal == MethodName.msme_extract_captcha:
                image_bytes = document_processing_service.get_image_bytes(source_url)
                resp = msme_captcha_extraction(image_bytes)
                extracted_captcha = resp['form']['prediction']
                
            data = {"job_id": str(job_id) , "prediction":extracted_captcha}
            response = format_response(detail_type="success", msg="instance_created", data=data)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=response,
            )
                
        except HTTPException:
            raise

        except Exception as e:
            error_msg = f"Facing error while create job: {e}"
            handle_error("exception_error","create_job_captcha",error_msg)
                 
    async def get_document(self,document_id, db: Session = Depends(get_db),user_id: str = Depends(authenticate)):
        """
        Retrieve a specific document by its ID.

        Args:
            document_id (str): ID of the document to be retrieved.
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            JSONResponse: Response with the document data or error message.
        """
        try:
            document_validate = JobDocumentService.authenticate_user_with_document(db,user_id,document_id)

            if not document_validate:
                logger(level='ERROR', status_code=403, message='Document ID does not belong to the authenticated user.',
                       endpoint=f'get_document')
                handle_error("invalid_document_id","get_document")

            documents = JobDocumentService.get_document_by_id(document_id, db)
            if not documents:
                logger(level="ERROR", status_code=404, message="Document not found",
                       endpoint="get_document")
                handle_error("document_not_found","get_document")

            job_responses = [
                DocumentsResponse(
                    job_id=str(document.job_id),
                    status=document.status,
                    document_name=document.document_name,
                    type=document.type,
                    result=json.loads(document.result) if document.result else None,
                    document_id=str(document.document_id),
                    page_number=document.page_number,
                    document_url=document_processing_service.generate_presigned_url(document.file_url),
                    updated_at=document.updated_at,
                    file_size=document.file_size,
                    pages=document.pages,
                    created_at=document.created_at
                )
                for document in documents
            ]
            resp_obj = DocumentsResponseList(data_list=job_responses)

            logger(level="INFO", status_code=200, message="record_fetched",
                   endpoint="get_document")

            return format_response(
                detail_type="success", data=resp_obj.data_list, msg="Record fetch successfully")

        except HTTPException:
            raise

        except Exception as e:
            error_msg = f"Facing error while get document: {e}"
            handle_error("exception_error","get_document",error_msg)

    async def get_job(self,job_id, db: Session = Depends(get_db),user_id: str = Depends(authenticate)):
        """
        Retrieve a specific job by its ID.

        Args:
            job_id (str): ID of the job to be retrieved.
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            JSONResponse: Response with the job data or error message.
        """
        try:
            job_validate = JobDocumentService.authenticate_user_with_job(db, user_id, job_id)
            if not job_validate:
                logger(level='ERROR', status_code=403, message='Job ID does not belong to the authenticated user.',
                    endpoint='get_job')
                handle_error("invalid_job_id", "get_job")
            
            job_data = JobDocumentService.get_job_by_id(job_id, db)
            job_data['job_id'] = job_data.pop('id')
            
            
            for source in job_data.get('source', []):
                source['document_id'] = source.pop('id')
                documents = JobDocumentService.get_document_by_id(source['document_id'], db)
                
                if not documents:
                    logger(level="ERROR", status_code=404, message="Document not found", endpoint="get_document")
                    handle_error("document_not_found","get_document")
                
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
                                else:
                                    logger(level="ERROR", status_code=500,
                                        message="Unexpected result format, expected a dictionary.",
                                        endpoint="get_document")
                        except json.JSONDecodeError as e:
                            logger(level="ERROR", status_code=500, 
                                message=f"Failed to parse document result JSON: {str(e)}",
                                endpoint="get_document")
                
                source['result'] = updated_results

            if not job_data['job_id']:
                message = "Job ID transformation failed: 'id' field is missing in job_data."
                handle_error("exception_error","get_job",message)
            
            for index, source in enumerate(job_data.get('source', [])):
                if not source.get('document_id'):
                    message = f"Source transformation failed at index {index}: 'id' field is missing in source."
                    handle_error("exception_error","get_job",message)
            
            job_item = JobsResponse(**job_data)
            job_item.created_at = document_processing_service.convert_to_ist(job_item.created_at)
            job_item.updated_at = document_processing_service.convert_to_ist(job_item.updated_at)
            job_item.job_start_time = document_processing_service.convert_to_ist(job_item.job_start_time)
            job_item.job_end_time = document_processing_service.convert_to_ist(job_item.job_end_time)
            
            response_data = JobsResponseList(data_list=[job_item])
            return format_response(detail_type="success", msg="record_fetched", data=response_data.data_list)

        except HTTPException:
            raise

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"An error occurred while get job: {e}"
            handle_error(error_type,"get_job",error_msg)

    async def get_all_jobs(self,
                       db: Session = Depends(get_db),
                       user_id: str = Depends(authenticate)):
        """
        Retrieve all jobs associated with the authenticated user.

        Args:
            db (Session): Database session.
            dependencies: JWT token dependencies.

        Returns:
            JSONResponse: Response with a list of jobs or error message.
        """
        try:
            jobs = JobDocumentService.get_job_by_user_id(user_id, db)

            job_responses = []
            for job in jobs:
                job['job_id'] = job.pop('id', None)

                for source in job.get('source', []):
                    source['document_id'] = source.pop('id', None)
                    documents = JobDocumentService.get_document_by_id(source['document_id'], db)
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
                                    else:
                                        logger(level="ERROR", status_code=500,
                                            message="Unexpected result format, expected a dictionary.",
                                            endpoint="get_all_jobs")
                            except json.JSONDecodeError as e:
                                logger(level="ERROR", status_code=500,
                                    message=f"Failed to parse document result JSON: {str(e)}",
                                    endpoint="get_all_jobs")
                    
                    source['result'] = updated_results

                if not job.get('job_id'):
                    raise ValueError(f"Job transformation failed: 'id' field is missing for job.")

                job_item = JobsResponse(**job)

                if job_item.created_at:
                    job_item.created_at = document_processing_service.convert_to_ist(job_item.created_at)
                if job_item.updated_at:
                    job_item.updated_at = document_processing_service.convert_to_ist(job_item.updated_at)
                if job_item.job_start_time:
                    job_item.job_start_time = document_processing_service.convert_to_ist(job_item.job_start_time)
                if job_item.job_end_time:
                    job_item.job_end_time = document_processing_service.convert_to_ist(job_item.job_end_time)

                job_responses.append(job_item)

            resp_obj = JobsResponseList(data_list=job_responses)
            return format_response(detail_type="success", msg="record_fetched", data=resp_obj.data_list)

        except HTTPException:
            raise

        except Exception as e:
            logger(level="CRITICAL", status_code=500,
                message=f"An error occurred while get all jobs: {e}",
                endpoint="get_all_jobs")
            raise HTTPException(status_code=500, detail="An internal error occurred.")

    async def delete_job(self,
                         job_id,
                        db: Session = Depends(get_db), 
                        user_id: str = Depends(authenticate),
                        
                        ):
        """
        Retrieve all jobs associated with the authenticated user or filter by job_name.

        Args:
            db (Session): Database session.
            user_id (str): The ID of the authenticated user.
            job_name (str, optional): Job name to filter jobs by.

        Returns:
            JSONResponse: Response with a list of jobs or a specific job if job_name matches.
        """
        try:
            delete_successful = JobDocumentService.delete_job_by_id(db, job_id)
            if delete_successful:
                message = f"Job {job_id} deleted successfully"
                logger(level="INFO", status_code=200, message=message, endpoint="delete_instance")
                data = {
                    "_id": str(job_id)
                }
                return format_response(detail_type="success", msg="record_deleted", data=data)

            else:
                logger(level="ERROR", status_code=500, message=f"Failed to delete instance {job_id}",
                    endpoint="delete_instance")
                handle_error("delete_instance_failed","delete_instance")
            
        except HTTPException:
            raise

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"An error occurred while delete job: {e}"
            handle_error(error_type,"delete_job",error_msg)

    async def get_method_list(self,
                            db: Session = Depends(get_db), 
                            user_id: str = Depends(authenticate)):
        
        try:
            logger(level="INFO", status_code=200,
                message=f"User id from Authentication: {user_id}", endpoint="get_method_list")
            
            method_list = JobDocumentService.get_method_list_from_db(db)
            methods_response = [MethodResponse(id=method['id'], display_name=method['display_name']) for method in method_list]
            return format_response(detail_type="success", msg="record_fetched", data=methods_response)

        except HTTPException:
            raise

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"An error occurred while get method list: {e}"
            handle_error(error_type,"get_method_list",error_msg)

    async def filter_jobs(self,
                         start_date: str = Query(None),
                         end_date: str = Query(None),
                         db: Session = Depends(get_db),
                         user_id: str = Depends(authenticate)):
        try:
            logger(level="INFO", status_code=200, message=f"Filtering jobs for user {user_id} between {start_date} and {end_date}", endpoint="filter_jobs")
            jobs = JobDocumentService.filter_jobs_by_date_from_db(db, user_id, start_date, end_date)
            
            job_responses = []
            for job in jobs:
                job['job_id'] = job.pop('id', None)

                for source in job.get('source', []):
                    source['document_id'] = source.pop('id', None)
                    documents = JobDocumentService.get_document_by_id(source['document_id'], db)
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
                                logger(level="ERROR", status_code=500, message=f"Failed to parse document result JSON: {str(e)}", endpoint="filter_jobs")
                    
                    source['result'] = updated_results

                if not job.get('job_id'):
                    continue

                job_item = JobsResponse(**job)

                if job_item.created_at:
                    job_item.created_at = document_processing_service.convert_to_ist(job_item.created_at)
                if job_item.updated_at:
                    job_item.updated_at = document_processing_service.convert_to_ist(job_item.updated_at)
                if job_item.job_start_time:
                    job_item.job_start_time = document_processing_service.convert_to_ist(job_item.job_start_time)
                if job_item.job_end_time:
                    job_item.job_end_time = document_processing_service.convert_to_ist(job_item.job_end_time)

                job_responses.append(job_item)

            resp_obj = JobsResponseList(data_list=job_responses)
            return format_response(detail_type="success", msg="record_fetched", data=resp_obj.data_list)
        except HTTPException:
            raise
        except Exception as e:
            handle_error("exception_error", "filter_jobs", f"Error filtering jobs: {e}")
