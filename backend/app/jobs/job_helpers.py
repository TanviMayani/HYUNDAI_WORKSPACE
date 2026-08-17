"""
This module provides the `DocumentProcessingService` class for handling various document processing tasks.

Key Features:
- Handles document uploads to AWS S3 and generates presigned URLs for access.
- Extracts data from PDF and image documents, including page count and content extraction.
- Converts PDF pages to images for further processing.
- Interacts with external services like LLMs to extract structured data from documents.
- Comprehensive error handling and logging for troubleshooting.

Components:
- DocumentProcessingService: A service class for managing document uploads, conversions, and data extraction.
  - Methods include handling S3 operations, image and PDF processing, and LLM integration.

Dependencies:
- AWS Boto3 for S3 interactions.
- PyPDF2 for PDF reading.
- Fitz for PDF to image conversion.
- FastAPI for exception handling.
- Local modules for logging and database interactions.

Error Handling:
- Custom HTTP exceptions for error scenarios.
- Detailed logging of operations and failures for debugging.

Usage:
- Initialize `DocumentProcessingService` to use its methods for document processing tasks.
"""

# Standard Library Imports
import io
import os
import re
import json
import jwt
import uuid
import tempfile
import mimetypes
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, unquote

# Third-Party Libraries
import fitz
import cv2
import boto3
import PyPDF2
import requests
import numpy as np
from PIL import Image
from qreader import QReader
from pyzbar.pyzbar import decode
from rapidfuzz.distance import Levenshtein
from pdf2image import convert_from_path,convert_from_bytes

# Local Application Imports
import easyocr
import pdfplumber
from app.logging_utils import logger
from .jobs_access import JobDocumentService
from .extract_llm import document_llm_service
from app.helpers import load_error_details, handle_error, find_best_match, find_best_match_account, find_best_match_irn, rotate_and_enhance_image_for_ocr
from .extract_captcha import msme_captcha_extraction
from app.models import Documents as ModelDocuments, Jobs as ModelJobs, MethodName, Status

reader = easyocr.Reader(['en'], gpu=False, recog_network='english_g2')
UPLOAD_BASE_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)

class DocumentProcessingService:
    """
    A service class for processing documents, including S3 operations, data extraction, and PDF/image handling.
    """
    def __init__(self):
        """
        Initialize the DocumentProcessingService with AWS and error configuration.

        Loads environment variables, error details, and initializes boto3 clients.
        """
        self.error_details = load_error_details("error_details.json")
        self.region_name = os.getenv("REGION_NAME")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.s3_client = None
        self.s3_resource = None
        if self.aws_access_key_id and self.aws_secret_access_key and self.region_name:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name,
                )
                self.s3_resource = boto3.resource(
                    "s3",
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name,
                )
            except Exception as exc:
                logger(level='WARNING', status_code=200, message=f"S3 client init skipped: {exc}", endpoint='DocumentProcessingService.__init__')
        self.qreader = QReader(model_size='l')
        self.invoice_set = {"Tax Invoice", "TAX-INVOICE", "INVOICE", "GST INVOICE", "EInvoice", "e-Invoice", "GSTInvoice", "E Invoice", "TaxInvoice", "CreditNote", "Credit Note", "Credit-Note"}

    @staticmethod
    def convert_to_ist(dt: datetime) -> datetime:
        """
        Convert a datetime object to Indian Standard Time (IST).

        Args:
            dt (datetime): The datetime object to convert.

        Returns:
            datetime: The converted datetime object in IST.
        """
        return dt

    def save_uploaded_bytes(self, filename, file_content, job_id):
        safe_name = os.path.basename(filename or "upload")
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", safe_name)
        upload_dir = os.path.join(UPLOAD_BASE_DIR, str(job_id))
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, safe_name)
        with open(file_path, "wb") as handle:
            handle.write(file_content)
        return file_path

    def generate_presigned_url(self, s3_url, expiration=604800):
        """
        Generate a presigned URL for accessing an S3 object.

        Args:
            s3_url (str): The S3 URL of the object.
            bucket_name (str): The S3 bucket name.
            expiration (int): URL expiration time in seconds. Defaults to 604800 (7 days).

        Returns:
            str: The presigned URL.
        """
        supported_image_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".json": "application/json",
            ".pdf": "application/pdf",
        }
        
        if s3_url.startswith("s3://"):
            parsed_url = urlparse(s3_url)
            bucket_name = parsed_url.netloc
            object_key = parsed_url.path.lstrip('/')
            file_extension = object_key.split('.')[-1].lower()
            if f".{file_extension}" in supported_image_types:
                content_type = supported_image_types[f".{file_extension}"]
            else:
                content_type, _ = mimetypes.guess_type(object_key)
                if content_type is None:
                    content_type = "application/octet-stream"
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key, "ResponseContentDisposition": "inline", "ResponseCacheControl": "no-store", "ResponseContentType": content_type},
                ExpiresIn=expiration,
            )
            return presigned_url
        
        parsed_url = urlparse(s3_url)
        if parsed_url.query:
            object_key = unquote(parsed_url.path.lstrip('/'))
            file_extension = object_key.split('.')[-1].lower()
            if f".{file_extension}" in supported_image_types:
                content_type = supported_image_types[f".{file_extension}"]
            else:
                content_type, _ = mimetypes.guess_type(object_key)
                if content_type is None:
                    content_type = "application/octet-stream"
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key, "ResponseContentDisposition": "inline", "ResponseCacheControl": "no-store",  "ResponseContentType": content_type},
                ExpiresIn=expiration,
            )
            return presigned_url

        pattern = r"https://(?P<bucket_name>[^.]+)\.s3\.amazonaws\.com/(?P<object_key>.+)"
        s3_match = re.match(pattern, s3_url)

        if s3_match:
            bucket_name = s3_match.group("bucket_name")
            object_key = unquote(s3_match.group("object_key"))
            file_extension = object_key.split('.')[-1].lower()
            if f".{file_extension}" in supported_image_types:
                content_type = supported_image_types[f".{file_extension}"]
            else:
                content_type, _ = mimetypes.guess_type(object_key)
                if content_type is None:
                    content_type = "application/octet-stream"
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key, "ResponseContentDisposition": "inline", "ResponseCacheControl": "no-store", "ResponseContentType": content_type},
                ExpiresIn=expiration,
            )
            return presigned_url

        if isinstance(s3_url, str):
            clean_str = s3_url.replace("file:///", "").replace("\\", "/")
            if "uploads/" in clean_str:
                rel_path = clean_str[clean_str.find("uploads/"):]
                server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
                return f"{server_base_url.rstrip('/')}/{rel_path}"

        return s3_url

    def get_pdf_page_count(self, bucket_name, document_name):
        """
        Get the number of pages in a PDF document stored in S3.

        Args:
            bucket_name (str): The S3 bucket name.
            document_name (str): The name of the document in S3.

        Returns:
            int: The number of pages in the PDF.
        """
        try:
            if os.path.exists(document_name):
                with open(document_name, "rb") as handle:
                    pdf_data = handle.read()
            elif self.s3_resource and bucket_name and document_name:
                obj = self.s3_resource.Bucket(bucket_name).Object(document_name)
                pdf_data = obj.get()["Body"].read()
            else:
                raise FileNotFoundError(f"File not found: {document_name}")
            if not pdf_data:
                error_type = "empty_file_error"
                error_msg = f"File {document_name} is empty."
                handle_error(error_type, "get_pdf_page_count", error_msg)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            if pdf_reader.is_encrypted:
                result = pdf_reader.decrypt("")
                if result == 0:
                    error_type = "password_protected_pdf_error"
                    error_msg = f"File {document_name} is password protected and cannot be processed."
                    handle_error(error_type, "get_pdf_page_count", error_msg)
            return len(pdf_reader.pages)
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error getting PDF page count: {e}", endpoint='get_pdf_page_count')
            raise

    def url_to_image_path(self, presigned_url: str) -> str:
        """
        Download a file from a presigned URL and save it locally.

        Args:
            presigned_url (str): The presigned URL of the file.

        Returns:
            str: The local file path of the downloaded file.
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
            handle_error("exception_error","url_to_image_path","The provided URL must start with 'https://' or 'http://' or be a local file path")

        temp_folder_path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        os.makedirs(temp_folder_path)
        temp_file_path = os.path.join(temp_folder_path, f"{uuid.uuid4().hex}.png")

        try:
            response = requests.get(presigned_url)
            response.raise_for_status()
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            return temp_file_path
        except Exception as e:
            # os.remove(temp_file_path)
            handle_error("exception_error","url_to_image_path",f"Failed to download file from presigned URL: {e}")

    @staticmethod
    def url_to_s3_uri(s3_url):
        """
        Convert an S3 URL to an S3 URI format.

        Args:
            s3_url (str): The S3 URL to convert.

        Returns:
            str: The converted S3 URI.
        """
        try:
            parsed_url = urlparse(s3_url)
            bucket_name = parsed_url.netloc.split(".")[0]
            object_key = unquote(parsed_url.path[1:])
            return f"s3://{bucket_name}/{object_key}"
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error converting URL to S3 URI: {e}", endpoint='url_to_s3_uri')
            raise

    @staticmethod
    def get_uuid() -> str:
        """
        Generate a unique UUID.

        Returns:
            str: The generated UUID.
        """
        return str(uuid.uuid4())

    @staticmethod
    def get_mimetypes(filename):
        """
        Get the MIME type of a file based on its name.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The MIME type of the file.
        """
        try:
            mime_type, _ = mimetypes.guess_type(filename)
            return mime_type
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error getting MIME type: {e}", endpoint='get_mimetypes')
            raise
          
    def get_s3_file_info(self, s3_uri: str):
        if os.path.exists(s3_uri):
            file_name = os.path.basename(s3_uri)
            file_size = os.path.getsize(s3_uri)
            return file_name, file_size, s3_uri, "local"

        parsed_uri = urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        s3_key = parsed_uri.path.lstrip('/')  
        file_name = os.path.basename(s3_key)
        logger(level='INFO', status_code=200, message=f"File name: '{file_name}', Bucket name:'{bucket_name}', S3 Key: '{s3_key}'", endpoint='get_s3_file_info')

        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            file_size = response['ContentLength']
            return file_name, file_size, s3_key, bucket_name
        
        except self.s3_client.exceptions.NoSuchKey:
            logger(level='CRITICAL', status_code=500, message=f"Error: File '{s3_key}' does not exist in bucket '{bucket_name}'.", endpoint='get_s3_file_info')
            return None, None, None, None
        
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"An error occurred: {e}", endpoint='get_s3_file_info')
            return None, None, None, None
    
    def file_to_presigned_url(self, filename, file_content, bucket_name, job_id):
        """
        Upload a file to S3 and generate a presigned URL.

        Args:
            filename (str): The name of the file.
            file_content (bytes): The content of the file.
            bucket_name (str): The S3 bucket name.
            job_id (str): The associated job ID.

        Returns:
            str: The presigned URL of the uploaded file.
        """
        try:
            supported_image_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".json": "application/json",
                ".pdf": "application/pdf"

            }
            file_extension = filename.lower().split('.')[-1]
            logger(level="INFO", status_code=200, message=f"getting file extension: {file_extension}",endpoint="file_to_presigned_url")

            if file_extension in supported_image_types:
                content_type = supported_image_types[f".{file_extension}"]
            else:
                content_type, _ = mimetypes.guess_type(filename)
                if content_type is None:
                    content_type = "application/octet-stream"

            object_key = f"hiibprod/WorkArea/Upload/{job_id}/{filename}"
            self.s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=file_content, ContentType=content_type, ContentDisposition="inline")
            presigned_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
            return presigned_url
        except Exception as e:
            error_message = f"Error in file upload: {e}"
            logger(level='CRITICAL', status_code=500, message=error_message, endpoint='file_to_presigned_url')
            return None

    def upload_to_s3(self, file, filename, job_id):
        """
        Upload a file to S3 and return its public URL.

        Args:
            file: The file object to upload.
            filename (str): The name of the file.
            job_id (str): The job ID for context.

        Returns:
            str: The public URL of the uploaded file.
        """
        try:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            object_key = f"hiib_extract/{job_id}/extract{filename}"

            with open(filename, "rb") as f:
                self.s3_client.upload_fileobj(
                    f, self.bucket_name, object_key, ExtraArgs={"ContentType": content_type, "ContentDisposition": "inline"}
                )
            return f"https://{self.bucket_name}.s3.amazonaws.com/{object_key}"
        except Exception as e:
            logger(level='CRITICAL', status_code=500, message=f"Error in file upload: {e}", endpoint='upload_to_s3')
            return None

    @staticmethod
    def serialize_datetime(obj):
        """
        Serialize a datetime object to an ISO 8601 string.

        Args:
            obj (datetime): The datetime object to serialize.

        Returns:
            str: The ISO 8601 formatted datetime string.

        Raises:
            TypeError: If the object is not serializable.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        handle_error("exception_error","serialize_datetime",f"Type not serializable")

    def convert_page_to_jpg(self, page, job_id, page_number):
        """
        Convert a PDF page to a JPG image, preprocess it, and save it locally.
        Uses pdf2image to convert the page, then applies preprocessing.

        Args:
            page: The PDF page object (only for context, as pdf2image handles the conversion).
            job_id (str): The job ID for context.
            page_number (int): The page number for naming the file.
            scale (float): Scaling factor for the image. Defaults to 2.0.

        Returns:
            str: The file path of the enhanced JPG image.
        """
        try:
            img = np.array(page) 
            # img = self.preprocess_image(img)
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            enhanced_image_path = os.path.join(
                tempfile.gettempdir(), f"{page_number}_{job_id}_enhanced_image_{self.get_uuid()}.jpg"
            )
            cv2.imwrite(enhanced_image_path, img)

            return enhanced_image_path

        except Exception as e:
            logger(level='ERROR', status_code=500, message=f"Error converting and enhancing page to JPG: {e}", endpoint='convert_page_to_jpg')
            return ""
    
    @staticmethod
    def get_image_bytes(image_url: str) -> bytes:
        """
        Fetch image bytes from a local file path or a remote URL.
        """
        if not image_url:
            return b""

        clean_path = image_url.replace("file:///", "")
        if os.path.exists(clean_path):
            with open(clean_path, "rb") as handle:
                return handle.read()

        if "uploads/" in image_url.replace("\\", "/"):
            clean_rel = image_url.replace("\\", "/")
            rel = clean_rel[clean_rel.find("uploads/"):]
            local_p = os.path.join(os.getcwd(), rel)
            if os.path.exists(local_p):
                with open(local_p, "rb") as handle:
                    return handle.read()

        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    
    @staticmethod
    def get_final_irn(qr_value: str, irn: str, invoice_no, dealer_gstin, hiib_gstin, llm_extracted_irn, old_quantity=None):
        """
        Extracts and validates the IRN from a QR value (JWT token).  
        If the QR value is not a valid JWT, returns the given IRN directly.  
        If the decoded IRN does not match the function IRN, returns the QR IRN.  
        Otherwise, returns either one (as they are the same).

        Args:
            qr_value (str): JWT token containing the QR IRN.
            irn (str): Original IRN from the function input.

        Returns:
            tuple: (final_irn, final_invoice, final_dealer_gstin, final_hiib_gstin, final_quantity)
        """
        final_quantity = old_quantity
        try:
            if not qr_value or qr_value == []:
                return irn, invoice_no, dealer_gstin, hiib_gstin, final_quantity
            
            decoded_qr = jwt.decode(qr_value[0], options={"verify_signature": False})
            qr_data = json.loads(decoded_qr.get("data", "{}"))  

            qr_irn = qr_data.get("Irn")
            doc_no = qr_data.get("DocNo", "")
            seller_gstin = qr_data.get("SellerGstin", "")
            buyer_gstin = qr_data.get("BuyerGstin", "")
            item_cnt = qr_data.get("ItemCnt")

            if item_cnt is not None and (not final_quantity or final_quantity in ["", "-", "None", "null"]):
                final_quantity = str(item_cnt)
            
            logger(level='INFO', status_code=200, message=f"decoded_qr: {qr_data}", endpoint='get_final_irn')

            if doc_no and invoice_no:
                distance_inv = Levenshtein.distance(str(doc_no), str(invoice_no))
                logger(level='INFO', status_code=200, message=f"Distance Invoice: {distance_inv}", endpoint='get_final_irn')
                if distance_inv <= 2:
                    invoice_no = doc_no
                    
            if seller_gstin and dealer_gstin:
                distance_gstin = Levenshtein.distance(str(seller_gstin), str(dealer_gstin))
                logger(level='INFO', status_code=200, message=f"Distance GSTIN: {distance_gstin}", endpoint='get_final_irn')
                if distance_gstin <= 2:
                    dealer_gstin = seller_gstin
                    
            if buyer_gstin and hiib_gstin:
                distance_hiib_gstin = Levenshtein.distance(str(buyer_gstin), str(hiib_gstin))
                logger(level='INFO', status_code=200, message=f"Distance GSTIN: {distance_hiib_gstin}", endpoint='get_final_irn')
                if distance_hiib_gstin <= 2:
                    hiib_gstin = buyer_gstin
            
            if qr_irn and llm_extracted_irn:
                if qr_irn == llm_extracted_irn:
                    return qr_irn, invoice_no, dealer_gstin, hiib_gstin, final_quantity
                             
            if qr_irn and irn:
                distance_irn = Levenshtein.distance(str(qr_irn), str(irn))
                logger(level='INFO', status_code=200, message=f"Distance IRN: {distance_irn}", endpoint='get_final_irn')
                if distance_irn < 4:
                    return qr_irn, invoice_no, dealer_gstin, hiib_gstin, final_quantity
            
        except (jwt.DecodeError, jwt.ExpiredSignatureError, AttributeError, json.JSONDecodeError, TypeError) as e:
            logger(level='ERROR', status_code=500, message=f"QR Decode Error: {str(e)}", endpoint='get_final_irn')

        return irn, invoice_no, dealer_gstin, hiib_gstin, final_quantity
       

    def detect_qr_in_sections(self, image, sections=4):
        """Splits the image into sections and detects QR codes."""
        height, width = image.shape[:2]
        section_height = height // sections

        for i in range(sections):
            y_start = i * section_height
            y_end = (i + 1) * section_height
            cropped_section = image[y_start:y_end, :]

            decoded_text = self.qreader.detect_and_decode(image=cropped_section)

            if decoded_text and any(decoded_text):
                return decoded_text, cropped_section

        return None, None

    def extract_qr_from_page_image(self, image) -> list[str]:
        """
        Extracts QR code(s) directly from a PIL image page.
        """
        try:
            image_cv = np.array(image)
            image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

            decoded_text = self.qreader.detect_and_decode(image=image_rgb)
            if decoded_text and any(decoded_text):
                cleaned_text = (
                    decoded_text.strip() if isinstance(decoded_text, str)
                    else [text.strip() for text in decoded_text if isinstance(text, str)]
                )
                return [cleaned_text] if isinstance(cleaned_text, str) else list(cleaned_text)

            qr_codes = decode(image_cv)
            for qr_code in qr_codes:
                qr_data = qr_code.data.decode('utf-8')
                cleaned_qr_data = qr_data.strip() if isinstance(qr_data, str) else [text.strip() for text in qr_data]
                return [cleaned_qr_data] if isinstance(cleaned_qr_data, str) else list(cleaned_qr_data)

            # scan in sections
            qr_text, _ = self.detect_qr_in_sections(image_rgb)
            if qr_text is not None:
                if isinstance(qr_text, tuple):
                    qr_text = list(qr_text)
                if isinstance(qr_text, str):
                    return [qr_text.strip()]
                elif isinstance(qr_text, list):
                    return [text.strip() for text in qr_text if isinstance(text, str)]
        except Exception as e:
            logger(level="ERROR", status_code=500, message=f"Error extracting QR from image: {e}", endpoint="extract_qr_from_page_image")
        return []

    def extract_qr_from_pdf_bytes(self, temp_pdf_path):
        """
        Extracts the first valid QR code from PDF bytes.

        :param pdf_data: The raw bytes of the PDF file.
        :return: A list containing one valid QR code string or an empty list if none are found.
        """
        pages = convert_from_path(temp_pdf_path)

        for page_num, image in enumerate(pages):
            image_cv = np.array(image)
            image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

            decoded_text = self.qreader.detect_and_decode(image=image_rgb)
            if decoded_text and any(decoded_text): 
                cleaned_text = decoded_text.strip() if isinstance(decoded_text, str) else [text.strip() for text in decoded_text if isinstance(text, str)]
                return [cleaned_text] if isinstance(cleaned_text, str) else list(cleaned_text)
            else:
                qr_codes = decode(image_cv)
                for qr_code in qr_codes:
                    qr_data = qr_code.data.decode('utf-8')
                    cleaned_qr_data = qr_data.strip() if isinstance(qr_data, str) else [text.strip() for text in qr_data]
                    return [cleaned_qr_data] if isinstance(cleaned_qr_data, str) else list(cleaned_qr_data)
                
                
            logger(level='INFO', status_code=200, message=f"No QR Code found on page {page_num+1}, scanning in sections...", endpoint='extract_qr_from_pdf_bytes')
            qr_text, qr_section = self.detect_qr_in_sections(image_rgb)
            if qr_text:
                if isinstance(qr_text, tuple):
                    qr_text = list(qr_text)
                if isinstance(qr_text, str):
                    cleaned_qr_text = qr_text.strip()
                    return [cleaned_qr_text]
                elif isinstance(qr_text, list):
                    cleaned_qr_text = [text.strip() for text in qr_text if isinstance(text, str)]
                    return cleaned_qr_text
            
        return []

    def extract_qr_from_pdf_page(self, temp_pdf_path: str, page_num: int) -> list[str]:
        """
        Extracts QR code(s) from a specific page in a PDF file.

        :param temp_pdf_path: Path to the temporary PDF file.
        :param page_num: Zero-based index of the page to process.
        :return: A list containing one or more cleaned QR code strings, or an empty list.
        """
        try:
            pages = convert_from_path(temp_pdf_path, first_page=page_num + 1, last_page=page_num + 1)
            if not pages:
                return []

            image = pages[0]
            image_cv = np.array(image)
            image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

            decoded_text = self.qreader.detect_and_decode(image=image_rgb)
            if decoded_text and any(decoded_text):
                cleaned_text = (
                    decoded_text.strip() if isinstance(decoded_text, str)
                    else [text.strip() for text in decoded_text if isinstance(text, str)]
                )
                return [cleaned_text] if isinstance(cleaned_text, str) else list(cleaned_text)

            qr_codes = decode(image_cv)
            for qr_code in qr_codes:
                qr_data = qr_code.data.decode('utf-8')
                cleaned_qr_data = qr_data.strip()
                return [cleaned_qr_data]

            logger(level='INFO', status_code=200,
                message=f"No QR Code found on page {page_num + 1}, scanning in sections...",
                endpoint='extract_qr_from_pdf_page')

            qr_text, _ = self.detect_qr_in_sections(image_rgb)
            if qr_text is not None:
                if isinstance(qr_text, tuple):
                    qr_text = list(qr_text)
                if isinstance(qr_text, str):
                    return [qr_text.strip()]
                elif isinstance(qr_text, list):
                    return [text.strip() for text in qr_text if isinstance(text, str)]

        except Exception as e:
            logger(level='ERROR', status_code=500,
                message=f"Error processing page {page_num + 1}: {str(e)}",
                endpoint='extract_qr_from_pdf_page')

        return []


    def extract_from_digital_pdf(self, pdf_data, target_tax, target_branch, target_invoice_no):
        try:
            text = ""
            with fitz.open(stream=pdf_data, filetype="pdf") as doc:
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n" 
               
            logger(level='INFO', status_code=200, message=f"Extracted digital Text Pdf: {text}", endpoint='extract_from_digital_pdf')
            if not text.strip():
                return None, None, None, None

            return (
                self.extract_account_number_from_text(text),
                self.extract_combined_irn_from_text(text),
                self.extract_dealer_code_from_text(text),
                self.extract_tax_value_from_text(text, target_tax),
                self.extract_branch_name_from_text(text, target_branch),
                self.is_invoice_number_matched(text, target_invoice_no)
            )
        except Exception as e:
            raise handle_error("exception_error", "extract_from_digital_pdf", f"Digital extraction error: {e}")

    def should_update_taxable_value(self, final_resp: dict) -> bool:
        form = final_resp.get('form', {})

        tax_value = form.get('taxable_value')
        total_invoice_value = form.get('total_invoice_value')
        cgst_amount = form.get('cgst_amount')
        sgst_utgst_amount = form.get('sgst_utgst_amount')
        igst_amount = form.get('igst_amount')

        if tax_value is None or total_invoice_value is None:
            return False

        try:
            tax_value = float(tax_value)
            total_invoice_value = float(total_invoice_value)
            cgst_amount = float(cgst_amount) if cgst_amount is not None else 0.0
            sgst_utgst_amount = float(sgst_utgst_amount) if sgst_utgst_amount is not None else 0.0
            igst_amount = float(igst_amount) if igst_amount is not None else 0.0
        except (ValueError, TypeError):
            return False

        derived_taxable = total_invoice_value - (cgst_amount + sgst_utgst_amount + igst_amount)
        logger(level='INFO', status_code=200, message=f"Extracted Taxable value : {tax_value}, Calculated Taxable value: {derived_taxable}", endpoint='extract_from_scanned_pdf')
        if abs(tax_value - derived_taxable) <= 1:
            return False
    
        if round(tax_value, 2) == round(derived_taxable, 2):
            return False

        return True
    
    def update_state_code(self, final_resp: dict):
        form = final_resp.get('form', {})

        dealer_state_code = form.get('hiib_state_code')
        pos = form.get('buyer_place_of_supply')
        
        if not dealer_state_code:
            if pos and pos.lower() in ["haryana", "harayana"]:
                return "06"
            
        return dealer_state_code

    def extract_from_scanned_pdf(self, pdf_data, target_tax, target_branch, target_invoice_no):
        try:
            t1 = datetime.now()
            images = []
            try:
                doc_fitz = fitz.open(stream=pdf_data, filetype="pdf")
                for page_num in range(len(doc_fitz)):
                    page_fitz = doc_fitz.load_page(page_num)
                    pix = page_fitz.get_pixmap(dpi=150)
                    img_data = pix.tobytes("png")
                    pil_img = Image.open(io.BytesIO(img_data))
                    images.append(pil_img)
                doc_fitz.close()
            except Exception as fitz_err:
                logger(level='WARNING', status_code=200, message=f"PyMuPDF scanned rendering failed: {fitz_err}; falling back to pdf2image.", endpoint='extract_from_scanned_pdf')
                images = convert_from_bytes(pdf_data)
            text = ""
            for idx, image in enumerate(images):
                if image.mode == "RGBA":
                    image = image.convert("RGB")
                max_size = 1200
                processed_image = rotate_and_enhance_image_for_ocr(image)
                if image.width > max_size or image.height > max_size:
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                result = reader.readtext(np.array(processed_image), detail=0)
                text += " ".join(result) + "\n"
                time.sleep(0.2)

            logger(level='INFO', status_code=200, message=f"Extracted text (scanned PDF - OCR) : {text}", endpoint='extract_from_scanned_pdf')
            logger(level='INFO', status_code=200, message=f"Taken time for OCR Scanned PDF time : {datetime.now() - t1}", endpoint='extract_from_scanned_pdf')
            return (
                self.extract_account_number_from_text(text),
                self.extract_combined_irn_from_text(text),
                self.extract_dealer_code_from_text(text),
                self.extract_tax_value_from_text(text, target_tax),
                self.extract_branch_name_from_text(text, target_branch),
                self.is_invoice_number_matched(text, target_invoice_no)
            )
        except Exception as e:
            logger(level='ERROR', status_code=500, message=f"OCR extraction error: {str(e)}", endpoint='extract_from_scanned_pdf')
            raise handle_error("exception_error", "extract_from_scanned_pdf", f"OCR extraction error: {str(e)}")

    def extract_tax_value_from_text(self, text: str, target_tax_value: str) -> str | None:
        """
        Extract the closest approximate tax value from the text.

        Args:
            text (str): The full text (e.g., invoice).
            target_tax_value (str): The expected tax value to compare against.
            threshold (float): Similarity threshold (default 0.95).

        Returns:
            str | None: Closest approximate match or None if no match is found.
        """
        if not target_tax_value:
            return None
        
        cleaned_text = re.sub(r'(\d),(\d)', r'\1\2', text)
        number_matches = re.findall(r'\d+\.\d{2}', cleaned_text)
        
        if not number_matches:
            return target_tax_value
        
        scored_matches = [(num, Levenshtein.distance(num, target_tax_value)) for num in number_matches]
        scored_matches.sort(key=lambda x: x[1])
        return scored_matches[0][0] if scored_matches else None
    
    def is_invoice_number_matched(self, text: str, invoice_no: str) -> bool:
        """
        Check if the given invoice number exactly matches any part of the provided text.

        Args:
            invoice_no (str): The invoice number to search for.
            text (str): The text content to search within (e.g., from OCR or document).

        Returns:
            bool: True if an exact match is found, otherwise False.
        """
        if not invoice_no or not text:
            return False

        invoice_no_clean = invoice_no.strip()
        text_clean = text.strip()

        pattern = rf'\b{re.escape(invoice_no_clean)}\b'
        return bool(re.search(pattern, text_clean, flags=re.IGNORECASE))

    def extract_branch_name_from_text(self, text: str, target_branch: str, max_distance: int = 1) -> str | None:
        """
        Extract the closest branch name from the text using Levenshtein distance.

        Args:
            text (str): Text extracted from the document.
            target_branch (str): Expected correct branch name.
            max_distance (int): Maximum allowed Levenshtein distance.

        Returns:
            str | None: Closest matching branch name or None.
        """
        if not target_branch:
            return None
        
        cleaned_text = re.sub(r'\s+', ' ', text.upper()).strip()
        words = cleaned_text.split()
        target_word_count = len(target_branch.split())

        for i in range(len(words) - target_word_count + 1):
            phrase = ' '.join(words[i:i + target_word_count])
            distance = Levenshtein.distance(phrase, target_branch)
            if distance <= max_distance:
                return phrase
            
        return None
        
    def extract_account_number_from_text(self, text: str):
        try:
            matches = re.findall(r'\b\d{11,17}\b', text)
            return list(set(matches)) if matches else []
        
        except Exception as e:
            raise handle_error("exception_error","extract_account_number_ocr",f"Error in extract_account_number_ocr: {str(e)}")
        
    def extract_combined_irn_from_text(self, text: str):
        try:
            # Matches 64 hexadecimal characters, optionally separated by hyphens or spaces
            IRN_PATTERN = re.compile(r"\b(?:[a-f0-9][-\s]*){63}[a-f0-9]\b", re.IGNORECASE)
            INVOICE_PATTERN = re.compile(r"\b(?:Tax Invoice|TAX-INVOICE|INVOICE|GST INVOICE|EInvoice|e-Invoice|GSTInvoice|E Invoice|TaxInvoice|CreditNote|Credit Note|Credit-Note)\b", re.IGNORECASE)

            matches = IRN_PATTERN.findall(text)
            # Remove whitespace AND hyphens so the final string is exactly 64 characters
            irns = [re.sub(r'[-\s]+', '', match) for match in matches]

            invoice_matches = INVOICE_PATTERN.findall(text)
            invoice_result = None
            if invoice_matches:
                non_invoice_matches = [m for m in invoice_matches if m.strip().upper() != "INVOICE"]
                invoice_result = non_invoice_matches[0] if non_invoice_matches else invoice_matches[0]
                logger(level='INFO', status_code=200, message=f"non_invoice_matches: {non_invoice_matches}", endpoint='extract_combined_irn_from_pdf')

            logger(level='INFO', status_code=200, message=f"invoice_matches: {invoice_matches}", endpoint='extract_combined_irn_from_pdf')
            
            if irns:
                return [irns[0]], invoice_result
            return [], invoice_result

        except Exception as e:
            raise handle_error("exception_error","extract_combined_irn_from_pdf",f"Error in extract_combined_irn_from_pdf: {str(e)}")
        
    def extract_dealer_code_from_text(self, text: str):
        try:
            matches = re.findall(r'\b[A-Z]\d{4}\b', text)
            return [matches[0]] if matches else []

        except Exception as e:
            raise handle_error("exception_error", "extract_dealer_code_from_pdf", f"Error: {str(e)}")
        
    def extract_data(self, file_name, method, s3_object, document_type, source_url, bucket_name, document_name,
                     document_id, job_id, db, total_files, num_pages, file_size, file):
        """
        Extract data from a document using specified methods and update the database.

        Args:
            file_name (str): The name of the file.
            method (str): The extraction method to use.
            s3_object: The S3 object reference.
            document_type (str): The type of the document (e.g., PDF, PNG).
            source_url (str): The source URL of the document.
            bucket_name (str): The S3 bucket name.
            document_name (str): The name of the document in S3.
            document_id (str): The unique ID of the document.
            job_id (str): The associated job ID.
            db (Session): The database session.
            total_files (int): The total number of files in the job.
            num_pages (int): The number of pages in the document.
            file_size (int): The size of the file in bytes.

        Raises:
            HTTPException: If any error occurs during processing.
        """
        try:
            from app.config import SessionLocal
            db = SessionLocal()
            time1 = datetime.now()
            s3 = self.s3_resource

            if document_type == "application/pdf":
                if os.path.exists(source_url):
                    with open(source_url, "rb") as handle:
                        pdf_data = handle.read()
                elif s3 and bucket_name and document_name:
                    bucket = s3.Bucket(bucket_name)
                    obj = bucket.Object(document_name)
                    pdf_data = obj.get()["Body"].read()
                else:
                    raise FileNotFoundError(f"Could not read PDF from {source_url}")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
                    temp_pdf_path = temp_pdf_file.name
                    temp_pdf_file.write(pdf_data)
                logger(level='INFO', status_code=200, message=f"temp_pdf_file: {temp_pdf_path}", endpoint='extract_data')
                pages = []
                try:
                    doc_fitz = fitz.open(temp_pdf_path)
                    for page_num in range(len(doc_fitz)):
                        page_fitz = doc_fitz.load_page(page_num)
                        pix = page_fitz.get_pixmap(dpi=300)
                        img_data = pix.tobytes("png")
                        pil_img = Image.open(io.BytesIO(img_data))
                        pages.append(pil_img)
                    doc_fitz.close()
                except Exception as fitz_err:
                    logger(level='WARNING', status_code=200, message=f"PyMuPDF rendering failed: {fitz_err}; falling back to pdf2image.", endpoint='extract_data')
                    pages = convert_from_path(temp_pdf_path, 300)
 
                extracted_data = {}
                important_keys = {"taxable_value", "cgst_amount", "sgst_utgst_amount", "igst_amount", "total_invoice_value","consigner_address", "consigner_place_of_supply"}
                for i, page in enumerate(pages):
                    jpg_path = self.convert_page_to_jpg(page, job_id, i)
                    logger(level='INFO', status_code=200, message=f"pages : {i}, jpg_path: {jpg_path}", endpoint='extract_data')
                    file_url  = source_url
                    # file_url = self.upload_to_s3(jpg_path, jpg_path, job_id) if len(pages) != 1 else source_url

                    with open(jpg_path, 'rb') as image_file:
                        image_bytes = image_file.read()

                    if method == MethodName.llm:
                        resp,input_tokens,output_tokens = document_llm_service.form_extract_llm(image_bytes, page, i)
                        
                    logger(level='INFO', status_code=200, message=f"document_id_new: {document_id}", endpoint='extract_data')
                    json_string = json.dumps(resp, default=self.serialize_datetime)
                    resp = resp["form"]
                    for key, value in resp.items():
                        if key not in extracted_data:
                            extracted_data[key] = value
                        elif key in important_keys:
                            if value not in [None, "", []]:
                                extracted_data[key] = value
                                logger(level='INFO', status_code=200, message=f"Updated key: {key} with new value", endpoint='extract_data')
                            else:
                                logger(level='INFO', status_code=200, message=f"Skipping key: {key} as new value is null/empty", endpoint='extract_data')
                        elif extracted_data[key] in [None, "", []] and value not in [None, "", []]:
                            extracted_data[key] = value
                            logger(level='INFO', status_code=200, message=f"Updated key: {key} with new non-null value", endpoint='extract_data')
                        else:
                            logger(level='INFO', status_code=200, message=f"Skipping key: {key} with existing non-null value", endpoint='extract_data')
                    qr_value = extracted_data.get('qr_value')
                    if not qr_value:
                        extracted_data['qr_value'] = self.extract_qr_from_page_image(page)
                        
                final_resp = {"form":extracted_data}
                qr_value = final_resp.get('form', {}).get('qr_value')
                if not qr_value:
                    final_qr = []
                    for page_img in pages:
                        qrs = self.extract_qr_from_page_image(page_img)
                        if qrs and any(qrs):
                            final_qr = qrs
                            break
                    final_resp['form']['qr_value'] = final_qr
                           
                logger(level="INFO", status_code=400, message=f"Total pages : {len(pages)}..", endpoint="form_extract_llm")
                
                if len(pages) in (1, 2, 3):
                    tax_value = final_resp.get('form', {}).get('taxable_value')
                    branch_name = final_resp.get('form', {}).get('branch')
                    hiib_state_code = final_resp.get('form', {}).get('hiib_state_code')
                    invoice_no = final_resp.get('form', {}).get('invoice_no')
                    
                    #IMPLEMENTED LOGIC OF ACCOUNT NUMBER
                    acc_digital, irn_digital, dealer_digital, final_tax_value, final_branch_name, is_match_invoice = self.extract_from_digital_pdf(pdf_data, tax_value, branch_name, invoice_no)
                    logger(level='INFO', status_code=200, message=(
                                        f"acc_digital: {acc_digital} | "
                                        f"irn_digital: {irn_digital} | "
                                        f"dealer_digital: {dealer_digital} | "
                                        f"final_tax_value: {final_tax_value} | "
                                        f"final_branch_name: {final_branch_name} |"
                                        f"is_match_invoice: {is_match_invoice} " ) ,endpoint='extract_data')

                    if not (acc_digital and irn_digital and dealer_digital):
                        logger(level='INFO', status_code=200, message="Falling back to OCR-based extraction.", endpoint='extract_data')
                        acc_digital, irn_digital, dealer_digital, final_tax_value, final_branch_name, is_match_invoice = self.extract_from_scanned_pdf(pdf_data, tax_value, branch_name, invoice_no)
                        logger(level='INFO', status_code=200, message=(
                                        f"acc_scanner: {acc_digital} | "
                                        f"irn_scanner: {irn_digital} | "
                                        f"dealer_scanner: {dealer_digital} | "
                                        f"final_tax_value_scanner: {final_tax_value} | "
                                        f"final_branch_name_scanner: {final_branch_name} |"
                                        f"is_match_invoice: {is_match_invoice} " ) ,endpoint='extract_data')
                        source = "scanned"
                    else:
                        source = "digital"

                    tax_correct = self.should_update_taxable_value(final_resp)
                    correct_state_code = self.update_state_code(final_resp)
                    logger(level='INFO', status_code=200, message=f"Extracted using: {source}, Tax Validation: {tax_correct}", endpoint='extract_data')
                    
                    if not hiib_state_code:
                        final_resp['form']['hiib_state_code'] = correct_state_code
                        logger(level='INFO', status_code=200, message=f"HIIB State Code Before : {hiib_state_code}, Updated: {final_resp['form']['hiib_state_code']}", endpoint='extract_data')
                        
                    if tax_correct:
                        final_resp['form']['taxable_value'] = final_tax_value
                        
                    if branch_name and final_branch_name:
                        if source == "digital":
                            final_resp['form']['branch'] = final_branch_name
                            logger(level='INFO', status_code=200, message=f"Branch Name Before : {branch_name}, Updated: {final_resp['form']['branch']}", endpoint='extract_data')
                            
                    logger(level='INFO', status_code=200, message=f"Taxable value Before : {tax_value}, Updated: {final_resp['form']['taxable_value']}", endpoint='extract_data')
                        
                    # ACCOUNT NUMBER
                    logger(level='INFO', status_code=200, message=f"Account Number Extracted from OCR: {acc_digital}", endpoint='extract_data')
                    account_no_llm = final_resp.get('form', {}).get('account_no')
                    logger(level='INFO', status_code=200, message=f"Account Number Extracted from LLM: {account_no_llm}", endpoint='extract_data')

                    best_match = find_best_match_account(account_no_llm, acc_digital, extracted_data["ack_no"], extracted_data["micr_code"], extracted_data["telephone_number"], extracted_data["invoice_no"])
                    if source == "digital":
                        final_resp['form']['account_no'] = best_match
                        logger(level='INFO', status_code=200, message=f"Updating Account Number in Final Dict: {best_match}", endpoint='extract_data')

                    # IRN
                    doc_type = final_resp['form']['doc_type']
                    irn_list, invoice_result = irn_digital

                    if not doc_type or doc_type.lower() not in {item.lower() for item in self.invoice_set} or doc_type.lower()=="invoice":
                    # if doc_type not in self.invoice_set:
                        if invoice_result:
                            final_resp['form']['doc_type'] = invoice_result

                    logger(level='INFO', status_code=200, message=f"IRN Number Extracted from OCR: {irn_list}", endpoint='extract_data')
                    logger(level='INFO', status_code=200, message=f"LLM Extracted Doc type : {doc_type}, Updated: {final_resp['form']['doc_type']}", endpoint='extract_data')
                    logger(level='INFO', status_code=200, message=f"IRN Number Extracted from LLM: {final_resp['form'].get('irn')}", endpoint='extract_data')
                    
                    llm_extracted_irn = final_resp['form'].get('irn')
                    best_match_irn = find_best_match_irn(final_resp['form'].get('irn'), irn_list)
                    final_resp['form']['irn'] = best_match_irn
                    logger(level='INFO', status_code=200, message=f"Updating IRN Number in Final Dict: {best_match_irn}", endpoint='extract_data')

                    # DEALER CODE
                    dealer_code_no_llm = final_resp.get('form', {}).get('dealer_code')
                    logger(level='INFO', status_code=200, message=f"Dealer Number Extracted from OCR: {dealer_digital}", endpoint='extract_data')
                    logger(level='INFO', status_code=200, message=f"Dealer Number Extracted from LLM: {dealer_code_no_llm}", endpoint='extract_data')
                    best_match_dealer_code = find_best_match(dealer_code_no_llm, dealer_digital, extracted_data["invoice_no"])
                    final_resp['form']['dealer_code'] = best_match_dealer_code
                    logger(level='INFO', status_code=200, message=f"Updating Dealer Number in Final Dict: {best_match_dealer_code}", endpoint='extract_data')

                form_data = final_resp.get('form', {})
                old_irn = form_data.get('irn')
                old_invoice = form_data.get('invoice_no')
                old_dealer_gstin = form_data.get('dealer_gstin')
                old_hiib_gstin = form_data.get('hiib_gstin')

                old_quantity = form_data.get('quantity')
                final_irn, final_invoice, final_dealer_gstin, final_hiib_gstin, final_quantity = self.get_final_irn(form_data.get('qr_value'), old_irn, old_invoice, old_dealer_gstin, old_hiib_gstin, llm_extracted_irn, old_quantity)
                logger(level='INFO', status_code=200, message=f"OLD IRN: {old_irn}, NEW IRN: {final_irn}", endpoint='extract_data')
                logger(level='INFO', status_code=200, message=f"OLD Invoice: {old_invoice}, NEW Invoice: {final_invoice}", endpoint='extract_data')
                logger(level='INFO', status_code=200, message=f"OLD DEALER GSTIN: {old_dealer_gstin}, NEW DEALER GSTIN: {final_dealer_gstin}", endpoint='extract_data')
                logger(level='INFO', status_code=200, message=f"OLD HIIB GSTIN: {old_hiib_gstin}, NEW HIIB GSTIN: {final_hiib_gstin}", endpoint='extract_data')
                logger(level='INFO', status_code=200, message=f"OLD Quantity: {old_quantity}, NEW Quantity: {final_quantity}", endpoint='extract_data')
                final_resp['form']['irn'] = final_irn
                if not is_match_invoice:
                    final_resp['form']['invoice_no'] = final_invoice
                final_resp['form']['dealer_gstin'] = final_dealer_gstin
                final_resp['form']['hiib_gstin'] = final_hiib_gstin
                final_resp['form']['quantity'] = final_quantity
                
                dealer_pan = final_resp.get('form', {}).get('dealer_pan')
                pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
                
                if dealer_pan and final_dealer_gstin and len(final_dealer_gstin) == 15:
                    final_pan = final_dealer_gstin[2:12]
                    if re.fullmatch(pan_pattern, final_pan) and Levenshtein.distance(dealer_pan, final_pan) <= 1 :
                        final_resp['form']['dealer_pan'] = final_pan
                        logger(level='INFO', status_code=200, message=f"OLD PAN : {dealer_pan}, NEW PAN : {final_pan}", endpoint='extract_data')
                    
                logger(level='INFO', status_code=200, message=f"Overall total time taken: {datetime.now()- time1}", endpoint='extract_data')
                documents = JobDocumentService.add_document_to_db(
                    db=db,
                    job_id=job_id,
                    file_name=file_name,
                    file_size=file_size,
                    document_type=document_type,
                    status=Status.Completed,
                    num_pages=num_pages,
                    page_number=i+1,
                    json_string=json.dumps(final_resp, default=self.serialize_datetime),
                    document_id=document_id,
                    source_url=source_url,
                    file_url=file_url,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )
                if not documents:
                    error_type = "exception_error"
                    error_msg = f"Error while add document to database"
                    handle_error(error_type,"extract_data",error_msg)

            elif document_type in ["image/png", "image/jpeg", "image/jpg"]:
                num_pages = 1
                documents = JobDocumentService.add_document_to_db_pending(
                    db, job_id, file_name, file_size, document_type, Status.In_Process, num_pages, document_id,
                    source_url, source_url
                )
                input_tokens,output_tokens = None, None
                if method == MethodName.llm:
                    image_bytes = self.get_image_bytes(source_url)
                    image_array = np.array(Image.open(io.BytesIO(image_bytes)))
                    resp,input_tokens,output_tokens = document_llm_service.form_extract_llm(image_bytes,image_array,1)
                
                if method == MethodName.msme_extract_captcha:
                    image_bytes = document_processing_service.get_image_bytes(document_processing_service.generate_presigned_url(source_url))
                    resp = msme_captcha_extraction(image_bytes)
                    
                document_data = db.query(ModelDocuments).filter(ModelDocuments.document_id == document_id).first()
                json_string = json.dumps(resp, default=self.serialize_datetime)
                setattr(document_data, "result", json_string)
                setattr(document_data, 'page_number', 1)
                setattr(document_data, "status", Status.Completed)
                setattr(document_data, "input_tokens", input_tokens)
                setattr(document_data, "output_tokens", output_tokens)
                setattr(document_data, "updated_at", datetime.now())
                db.add(document_data)
                db.commit()

            document_processed = JobDocumentService.check_all_documents_processed(job_id, total_files, db)
            if document_processed:
                job = db.query(ModelJobs).filter(ModelJobs.id == job_id).first()
                setattr(job, "status", Status.Completed)
                setattr(job, "updated_at", datetime.now())
                setattr(job, "job_end_time", datetime.now())
                db.add(job)
                db.commit()
                JobDocumentService.process_job_completion(job_id, db)
                
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            logger(level='CRITICAL', status_code=500, message=f"Error extracting data: {e}\nTraceback:\n{tb_str}", endpoint='extract_data')
            document_data = db.query(ModelDocuments).filter(ModelDocuments.document_id == document_id).first()
            if document_data:
                setattr(document_data, "status", Status.Failed)
                setattr(document_data, "updated_at", datetime.now())
                db.add(document_data)
                db.commit()

            job = db.query(ModelJobs).filter(ModelJobs.id == job_id).first()
            if job:
                setattr(job, "status", Status.Failed)
                setattr(job, "updated_at", datetime.now())
                setattr(job, "job_end_time", datetime.now())
                db.add(job)
                db.commit()
            
            try:
                JobDocumentService.process_job_completion(job_id, db)
            except Exception as inner_e:
                logger(level='CRITICAL', status_code=500, message=f"Error in process_job_completion: {inner_e}", endpoint='extract_data')

            try:
                handle_error("exception_error","extract_data",f"Error extracting data: {e}")
            except Exception:
                pass # Swallowing HTTPException in background task so it doesn't crash the worker thread silently
        finally:
            db.close()

document_processing_service = DocumentProcessingService()