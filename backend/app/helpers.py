"""
This module provides utility functions for authentication, password hashing, token generation, and response formatting.

Key Features:
- JWT token creation and decoding for authentication.
- API key-based authentication support.
- Password hashing and verification using Argon2.
- Structured response formatting for API endpoints.
- Custom exception handling with detailed logging.

Components:
- `create_access_token`: Generates JWT tokens.
- `authenticate`: Handles user authentication via JWT or API key.
- `get_hashed_password`: Hashes passwords securely.
- `verify_password`: Verifies passwords against hashed values.
- Response formatting utilities: `format_response`, `exception_format_response`.

Dependencies:
- FastAPI for dependency injection and exception handling.
- SQLAlchemy for database interactions.
- `jose` for JWT encoding and decoding.
- `passlib` for password hashing.
- Logging utilities for detailed error and info logs.
- Python standard libraries for JSON, UUID, and datetime utilities.

Error Handling:
- Handles token expiration and decoding errors.
- Logs all authentication attempts and failures.
- Provides detailed error responses with traceback IDs.

Usage:
- Import and use the authentication and utility functions in your FastAPI application.
"""
# Standard Library Imports
import os
import json
import uuid
import logging
import re
import calendar
from typing import Union, Any
from datetime import datetime, timedelta
from rapidfuzz import process, fuzz
import pdfplumber
import re
import pytesseract
from pdf2image import convert_from_bytes

import io

# Third-Party Imports
import cv2
import easyocr
import numpy as np
from jose import jwt
from sqlalchemy.orm import Session
from PIL import Image, ImageEnhance
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Header
from rapidfuzz.distance import Levenshtein
from urllib.parse import urlparse

# Local Application Imports
from app.models import Keys
from app.config import get_db
from dotenv import load_dotenv
from app.token import JWTBearer
from app.logging_utils import logger

load_dotenv()
reader = easyocr.Reader(['en'])
password_context = CryptContext(schemes=["argon2"], deprecated="auto")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv(
    "REFRESH_TOKEN_EXPIRE_MINUTES") 
REFRESH_TOKEN_EXPIRE_MINUTES = int(REFRESH_TOKEN_EXPIRE_MINUTES)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_error_details(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

with open("response_messages.json", "r") as file:
    response_messages = json.load(file)

def format_month_year(date_str):
    if not date_str:
        return None  # Handle None or empty cases

    # Normalize input by removing special characters except letters and numbers
    cleaned_date = re.sub(r'[^A-Za-z0-9]', '', date_str).upper()

    # Extract month name (letters) and year (digits)
    match = re.match(r'([A-Za-z]+)(\d{2,4})$', cleaned_date)
    if match:
        month, year = match.groups()

        # Convert full month name to three-letter abbreviation
        month_abbr = None
        for i in range(1, 13):
            if month.startswith(calendar.month_name[i].upper()):  # Match full month name
                month_abbr = calendar.month_abbr[i].upper()
                break

        if not month_abbr:
            return date_str  # Return original input if month is invalid

        # Convert 2-digit year to 4-digit year (assuming 2000s)
        if len(year) == 2:
            year = f"20{year}"

        return f"{month_abbr}-{year}"

    return date_str  # Return original input if format is incorrect

def rearrange_bank_name(input_string: str) -> str:

    if "HDFC" in input_string.upper() or "hdfc" in input_string.lower():
        return "HDFC BANK"

    
def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    expires_delta: minute
    """
    logger(level='INFO', status_code=200,message=f'ACCESS_TOKEN_EXPIRE_MINUTES : {ACCESS_TOKEN_EXPIRE_MINUTES}',endpoint='/create_access_token')
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)

    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def format_response(
    detail_type=None, data=None, loc=None, msg=None, input_value=None, reason=None
):
    response_detail = {}
    if detail_type is not None:
        response_detail["type"] = detail_type
    if data is not None:
        response_detail["data"] = data
    if loc is not None:
        response_detail["loc"] = [loc]
    if msg is not None:
        response_detail["msg"] = response_messages.get(msg, msg)
    if input_value is not None:
        response_detail["input"] = input_value
    if reason is not None:
        response_detail["ctx"] = {"reason": reason}
    response_detail["traceback_id"] = str(uuid.uuid4())

    formatted_response = {"detail": [response_detail]}
    return formatted_response


def exception_format_response(
    detail_type=None, data=None, loc=None, msg=None, input_value=None, reason=None
):
    response_detail = {}
    if detail_type is not None:
        response_detail["type"] = detail_type
    if data is not None:
        response_detail["data"] = data
    if loc is not None:
        response_detail["loc"] = [loc]
    if msg is not None:
        response_detail["msg"] = msg
    if input_value is not None:
        response_detail["input"] = input_value
    if reason is not None:
        response_detail["ctx"] = {"reason": reason}
    response_detail["traceback_id"] = str(uuid.uuid4())

    formatted_response = response_detail
    return formatted_response


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

error_details = load_error_details("error_details.json")

def handle_error(error_type, endpoint, log_msg: str = None):
    log_msg = log_msg or error_details[error_type]["reason"]
    response = exception_format_response(
                    detail_type=error_details[error_type]["detail_type"],
                    msg=error_details[error_type]["msg"],
                    reason=error_details[error_type]["reason"],
                )
    traceback_id = response["traceback_id"]
    logger(level='CRITICAL', status_code=error_details[error_type]["status_code"], message=str(log_msg),
                        endpoint=endpoint,
                        traceback_id=traceback_id)
    raise HTTPException(
                    status_code=error_details[error_type]["status_code"],
                    detail=[response]
                )
    
def authenticate(
        db: Session = Depends(get_db),
        token: Union[str, None] = Depends(JWTBearer(auto_error=False)),
        x_api_key: str = Header(None)
) -> str:
    """
    Authenticate using JWT token or API key.

    Args:
        db (Session): Database session dependency.
        token (Union[str, None]): JWT token for authentication, or None if not provided.
        x_api_key (str): API key header for alternative authentication.

    Returns:
        str: The user_id if authentication is successful.

    Raises:
        HTTPException: If neither token nor API key is provided, or if the token or API key is invalid.
    """
    user_id = None

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
            user_id = payload["sub"]
            
        except HTTPException:
            raise

        except jwt.ExpiredSignatureError:
            handle_error("expire_error","authenticate")

        except jwt.JWTError:
            handle_error("decode_error","authenticate")

        except Exception as e:
            handle_error("exception_error","authenticate", f"An error occurred while authenticate: {e}")

    elif x_api_key:
        api_key_valid = db.query(Keys).filter_by(key=x_api_key, is_active=True).first()
        if not api_key_valid:
            handle_error("invalid_api_key","authenticate")
        user_id = str(api_key_valid.member_id)

    else:
        handle_error("missing_authentication_error","authenticate")

    return user_id

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def extract_account_number_ocr(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        account_pattern = re.compile(r'\b\d{11,17}\b')
        with open(file_path, 'rb') as handle:
            pdf_data = handle.read()
        extracted_account_numbers = []
        is_scanned = False 

        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    matches = account_pattern.findall(text)
                    if matches:
                        extracted_account_numbers.extend(matches)
                else:
                    is_scanned = True
                    
        if is_scanned or not extracted_account_numbers:
            images = convert_from_bytes(pdf_data) 
            for img in images:
                ocr_result  = reader.readtext(np.array(img), detail=0)
                ocr_text = " ".join(ocr_result)
                matches = account_pattern.findall(ocr_text)
                if matches:
                    extracted_account_numbers.extend(matches)          
        return extracted_account_numbers if extracted_account_numbers else []
    
    except Exception as e:
        raise handle_error("exception_error", "extract_account_number_ocr", f"Error in extract_account_number_ocr: {str(e)}")

def extract_combined_irn_from_pdf(file_path):
    """Extract and combine the first two matched IRN-like sequences from the first page of a local PDF file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        # Matches 64 hexadecimal characters, optionally separated by hyphens or spaces
        IRN_PATTERN = re.compile(r"\b(?:[a-f0-9][-\s]*){63}[a-f0-9]\b", re.IGNORECASE)
        INVOICE_PATTERN = re.compile(r"\b(?:Tax Invoice|TAX-INVOICE|INVOICE|GST INVOICE|EInvoice|e-Invoice|GSTInvoice|E Invoice|TaxInvoice|CreditNote|Credit Note|Credit-Note)\b", re.IGNORECASE)

        with open(file_path, 'rb') as handle:
            pdf_data = handle.read()
        extracted_text = ""
        
        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            first_page = pdf.pages[0] 
            extracted_text = first_page.extract_text() or ""  
            logger(level='INFO', status_code=200, message=f"Extracted digital Text from First Page IRN: {extracted_text}", endpoint='extract_combined_irn_from_pdf')

        invoice_result = None
        matches = IRN_PATTERN.findall(extracted_text)
        irns = [re.sub(r'[-\s]+', '', match) for match in matches]
        invoice_matches = INVOICE_PATTERN.findall(extracted_text)

        if not extracted_text.strip() or not irns:
            images = convert_from_bytes(pdf_data, first_page=0, last_page=1)  
            ocr_result  = reader.readtext(np.array(images[0]), detail=0)
            extracted_text = " ".join(ocr_result)

            logger(level='INFO', status_code=200, message=f"Extracted text (scanned PDF - OCR) IRN: {extracted_text}", endpoint='extract_combined_irn_from_pdf')
            matches = IRN_PATTERN.findall(extracted_text)
            irns = [re.sub(r'[-\s]+', '', match) for match in matches]
            if not invoice_matches:
                invoice_matches = INVOICE_PATTERN.findall(extracted_text)
        
        if invoice_matches:
            non_invoice_matches = [match for match in invoice_matches if match.strip().upper() != "INVOICE"]
            invoice_result = non_invoice_matches[0] if non_invoice_matches else invoice_matches[0]
            logger(level='INFO', status_code=200, message=f"non_invoice_matches: {non_invoice_matches}", endpoint='extract_combined_irn_from_pdf')
            
        logger(level='INFO', status_code=200, message=f"invoice_matches: {invoice_matches}", endpoint='extract_combined_irn_from_pdf')
        
        if irns:
            return [irns[0]], invoice_result
        else:
            return [], invoice_result
        
    except Exception as e:
        raise handle_error("exception_error", "extract_combined_irn_from_pdf", f"Error in extract_combined_irn_from_pdf: {str(e)}")
    
def remove_repeating_address(address, min_words=3, max_words=5):
    try:
        if not address:
            return address
        
        cleaned_address = address.replace('"', '')

        words = cleaned_address.split()
        if len(words) < min_words * 2:
            return address.strip()

        for word_count in range(min_words, max_words + 1):
            if len(words) < word_count * 2:
                continue

            anchor = " ".join(words[:word_count])

            first_occurrence = cleaned_address.find(anchor)
            second_occurrence = cleaned_address.find(anchor, first_occurrence + len(anchor))

            if second_occurrence != -1:
                return address[:second_occurrence].strip()
        
        return address.strip()

    except Exception as e:
        raise handle_error("exception_error", "remove_repeating_address", f"Error in remove_repeating_address: {str(e)}")

def extract_dealer_code_from_pdf(file_path):
    """Extract the dealer code (format: A1234) from the first page of a local PDF file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        DEALER_CODE_PATTERN = re.compile(r"\b[A-Z]\d{4}\b")

        with open(file_path, 'rb') as handle:
            pdf_data = handle.read()
        extracted_text = ""

        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            first_page = pdf.pages[0]  
            extracted_text = first_page.extract_text() or "" 
            
        dealer_codes = DEALER_CODE_PATTERN.findall(extracted_text)
        if not extracted_text.strip() or not dealer_codes:
            images = convert_from_bytes(pdf_data, first_page=0, last_page=1)  
            ocr_result  = reader.readtext(np.array(images[0]), detail=0)
            extracted_text = " ".join(ocr_result)

            dealer_codes = DEALER_CODE_PATTERN.findall(extracted_text)
    
        return [dealer_codes[0]] if dealer_codes else []
    
    except Exception as e:
        raise handle_error("exception_error", "extract_dealer_code_from_pdf", f"Error: {str(e)}")
     
def find_best_match(target_string, string_list, invoice_no):
    """
    Finds the best matching string from an array using RapidFuzz.
    :param target_string: The string to compare against.
    :param string_list: List of strings to find the best match.
    :return: Best matching string and its match percentage.
    """
    try: 
        if not string_list:
            return target_string
        
        if not target_string:
            return string_list[0]
        
        best_match = process.extractOne(target_string, string_list, scorer=fuzz.ratio)
        final_match = best_match[0] if best_match else target_string
        distance_dealer_code = Levenshtein.distance(target_string, final_match)
        logger(level='INFO', status_code=200, message=f"Distance Dealer code: {distance_dealer_code}", endpoint='get_final_irn')
        if invoice_no:
            if final_match in invoice_no:
                if distance_dealer_code <= 1:
                    return final_match
                return target_string
        
        logger(level='INFO', status_code=200, message=f"Final Match: {final_match}", endpoint='extract_combined_irn_from_pdf')
        return final_match
    
    except Exception as e:
        raise handle_error("exception_error","find_best_match",f"Error in find_best_match dealer code: {str(e)}")

def find_best_match_irn(target_string, string_list):
    """
    Finds the best matching string from an array using RapidFuzz.
    :param target_string: The string to compare against.
    :param string_list: List of strings to find the best match.
    :return: Best matching string and its match percentage.
    """
    try: 
        if not string_list:
            return target_string
        
        if not target_string:
            return target_string
        
        best_match = process.extractOne(target_string, string_list, scorer=fuzz.ratio)
        final_match = best_match[0] if best_match else target_string
        
        logger(level='INFO', status_code=200, message=f"Final Match IRN: {final_match}", endpoint='extract_combined_irn_from_pdf')
        return final_match
    
    except Exception as e:
        raise handle_error("exception_error", "find_best_match", f"Error in find_best_match IRN: {str(e)}")
    
def rotate_and_enhance_image_for_ocr(image_input):
    """
    Enhances and rotates an image (bytes or PIL Image) for better OCR results.

    Args:
        image_input (bytes or PIL.Image.Image): Image bytes or PIL Image.

    Returns:
        PIL.Image.Image: Rotated and enhanced image.
    """
    if image_input is None:
        logger(level='ERROR', status_code=500, message=f"Image Input is None", endpoint='rotate_and_enhance_image_for_ocr')
        return None
    try:
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError("Input must be bytes or PIL.Image.Image")

        if image.mode == "RGBA":
            image = image.convert("RGB")
        
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        rotation_angle = 0
        final_rotation_angle = 0
        max_confidence = 0.0
        
        for img_osd in [thresh, cv_image]:
            try:
                osd_data = pytesseract.image_to_osd(
                    img_osd, 
                    config='--psm 0', 
                    output_type=pytesseract.Output.DICT
                ) 
                current_angle = osd_data['rotate']
                current_conf = osd_data['orientation_conf']
                
                if current_conf > max_confidence:
                    max_confidence = current_conf
                    rotation_angle = current_angle
                    
            except Exception as e:
                logger(level='DEBUG', message=f"OSD attempt failed: {str(e)}")
        
        CONFIDENCE_THRESHOLD = 5.0
        if max_confidence > CONFIDENCE_THRESHOLD:
            final_rotation_angle = rotation_angle
        
        if final_rotation_angle == 90:
            image = image.transpose(Image.ROTATE_90)
        elif final_rotation_angle == 180:
            image = image.transpose(Image.ROTATE_180)
        elif final_rotation_angle == 270:
            image = image.transpose(Image.ROTATE_270)
            
        logger(level='INFO', status_code=200, message=f"final_rotation_angle:  {final_rotation_angle}", endpoint='extract_combined_irn_from_pdf')
        
        return image
    
    except Exception as e:
        logger(level='ERROR', status_code=500, 
               message=f"Image processing failed: {str(e)}", 
               endpoint='rotate_and_enhance_image_for_ocr')
        return None
    
def find_best_match_account(target_string, string_list, ack_no, micr_code, telephone_number, invoice_no):
    """
    Finds the best matching string from an array using RapidFuzz.
    :param target_string: The string to compare against.
    :param string_list: List of strings to find the best match.
    :return: Best matching string and its match percentage.
    """
    try: 
        if not string_list:
            return target_string
        
        if not target_string:
            return target_string
            
        best_match = process.extractOne(target_string, string_list, scorer=fuzz.ratio)
        final_match = best_match[0] if best_match else target_string
        if final_match == ack_no or final_match == micr_code or final_match == telephone_number or final_match == invoice_no:
            return target_string
        
        logger(level='INFO', status_code=200, message=f"Final Match Account: {final_match}", endpoint='extract_combined_irn_from_pdf')
        return final_match
    
    except Exception as e:
        raise handle_error("exception_error", "find_best_match", f"Error in find_best_match Account: {str(e)}")