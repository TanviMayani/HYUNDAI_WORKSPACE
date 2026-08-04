"""Defines Pydantic models for API request and response data."""

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class DocumentsResponse(BaseModel):
    """
    Pydantic model for document response.

    Attributes:
        id (str): The unique identifier for the document.
        job_id (str): The ID of the job associated with the document.
        status (str): The current status of the document (e.g., 'completed', 'pending').
        name (str): The name of the document.
        type (str): The type of the document (e.g., PDF, DOCX).
        result (Optional[Dict[str, Any]]): The result of processing the document, if applicable.
        document_id (str): A unique identifier for the document.
        page_number (Optional[int]): The page number of the document being referenced.
        document_url (str): The URL where the document is stored.
        updated_at (datetime): The timestamp of the last update made to the document.
        file_size (Optional[int]): The size of the document file in bytes.
        pages (Optional[int]): The total number of pages in the document.
        created_at (datetime): The timestamp when the document was created.
    """
    job_id: str
    status: str
    document_name: str
    type: str
    result:Optional[Dict[str, Any]]
    document_id: str
    page_number: Optional[int] = None
    document_url: str
    updated_at: datetime
    file_size: Optional[int] = None
    pages: Optional[int] = None
    created_at: datetime

class DocumentsResponseList(BaseModel):
    """
    Pydantic model for a list of document responses.

    Attributes:
        data_list (List[DocumentsResponse]): A list of document responses.
    """

    data_list: List[DocumentsResponse]

class SourceItem(BaseModel):
    """
    Pydantic model for a source item in a job response.

    Attributes:
        id (str): The unique identifier for the source item.
        url (str): The URL of the source item.
        name (str): The name of the source item.
        total_page (int): The total number of pages in the source item.
        size (int): The size of the source item in bytes.
    """
    document_id: str
    url: str
    name: str
    total_page: int
    size: int
    result: Optional[List] = None

class JobsResponse(BaseModel):
    """
    Pydantic model for job response.

    Attributes:
        id (str): The unique identifier for the job.
        status (str): The current status of the job (e.g., 'running', 'completed').
        job_name (Optional[str]): The name of the job.
        method (Optional[str]): The method used for the job.
        job_start_time (datetime): The timestamp when the job started.
        job_end_time (Optional[datetime]): The timestamp when the job ended.
        process (str): The process associated with the job.
        source (List[SourceItem]): A list of sources associated with the job.
        extract (List[str]): A list of extracted information from the job.
        created_by (str): The identifier of the user who created the job.
        created_at (datetime): The timestamp when the job was created.
        updated_at (datetime): The timestamp when the job was last updated.
    """
    job_id: str
    status: str
    job_name: Optional[str]
    method: Optional[str]
    job_start_time: Optional[datetime]
    job_end_time: Optional[datetime]
    process: str
    source: List[SourceItem]
    created_by: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class JobsResponseList(BaseModel):
    """
    Pydantic model for a list of job responses.

    Attributes:
        data_list (List[JobsResponse]): A list of job responses.
    """
    data_list: List[JobsResponse]
    
class MethodResponse(BaseModel):
    """
    Pydantic model for method response.

    Attributes:
        id (str): The unique identifier for the method.
        display_name (str): The display name of the method.
    """
    id: str
    display_name: str
    
class MethodResponseList(BaseModel):
    """
    Pydantic model for a list of method responses.

    Attributes:
        methods (List[MethodResponse]): A list of method responses.
    """
    methods: List[MethodResponse]
