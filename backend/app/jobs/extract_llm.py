"""
This module provides the `DocumentLLMService` class, enabling structured data extraction from document images via Large Language Models (LLMs).

Key Features:
- Encodes document images into base64 and communicates with the LLM for structured data extraction.
- Supports single and multiple image processing.
- Extracts predefined fields and formats them in JSON.
- Handles comprehensive error logging and response validation.

Components:
- DocumentLLMService: A service class for interacting with LLMs.
  - `generate_response`: Generates a structured response for a single image.
  - `form_extract_llm`: Extracts structured data from a single image.
  - Utility methods for image encoding and JSON handling.

Dependencies:
- Boto3 for AWS S3 interactions.
- Anthropic API for communication with LLMs.
- FastAPI for HTTP exception handling.
- Local modules for logging utilities and error handling.

Error Handling:
- Custom HTTP exceptions for error scenarios.
- Detailed logging of operations and failures for debugging.

Usage:
- Initialize `DocumentLLMService` to use its methods for LLM-based data extraction.
"""

# Standard Library Imports
import os
import io
import re
import json
import base64

# Third-Party Libraries
import cv2
import numpy as np
from PIL import Image
from qreader import QReader
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

# Local Application Imports
from app.helpers import handle_error, rotate_and_enhance_image_for_ocr
from app.logging_utils import logger
from app.helpers import load_error_details, format_month_year, rearrange_bank_name, remove_repeating_address

class DocumentLLMService:
    """
    A class-based implementation for interacting with LLMs and extracting structured data from documents.
    """

    def __init__(self):
        load_dotenv()
        self.error_details = load_error_details("error_details.json")
        self.BUCKET_NAME = os.getenv("BINARY_BUCKET_NAME")
        self.use_external_llm = False
        self.external_llm_provider = os.getenv("EXTERNAL_LLM_PROVIDER", "").strip().lower()
        self.external_llm_api_key = os.getenv("EXTERNAL_LLM_API_KEY", "").strip()
        self.external_llm_model = os.getenv("EXTERNAL_LLM_MODEL", "").strip()
        self.external_llm_base_url = os.getenv("EXTERNAL_LLM_BASE_URL", "").strip()

        external_llm_enabled = os.getenv("EXTERNAL_LLM_ENABLED", "").strip().lower()
        if self.external_llm_provider and self.external_llm_api_key and self.external_llm_model:
            if external_llm_enabled in {"1", "true", "yes", "on"}:
                self.use_external_llm = True
            else:
                logger(level="INFO", status_code=200, message="External LLM is disabled by default; set EXTERNAL_LLM_ENABLED=true to enable it.", endpoint="__init__")

        self.qreader = QReader(model_size='l')

        self.SYSTEM_PROMPT = """
        You are a language model designed to extract structured data from documents. Given an image of a document, extract the information in the following format:

        1. **Form Extraction**: 
           - Extract the value for the following keys:
           - Extract the valid Bank Account Number with a reasonable length from Bank Details section ,do not modify numbers (e.g., bank account numbers must be extracted exactly as it is) Don't add addditional numbers. and Place it under the key 'A/c No' Strictly do not add extra digits or modify the sequence of numbers in any way.
           - For date format STRICTLY follow below Date Extraction Rule.
           - Extract the document heading (e.g., 'Tax Invoice', 'Credit Note', etc.) as the exact value for the 'Document Type' key.
           - Look for these words in the document for the 'Document Type' key: {"Tax Invoice", "TAX-INVOICE", "INVOICE", "GST INVOICE", "EInvoice", "e-Invoice", "GSTInvoice", "E Invoice", "TaxInvoice", "CreditNote", "Credit Note", "Credit-Note"}. If "INVOICE" and any other value are found, return the other value; if only "INVOICE" is found, return it; if none are found, return the header value; if header is missing, return null.
           - When "HIIB" is mentioned, it refers to "hyundai india insurance broking".
           - In Period of service Ensure that when a month is mentioned in short form (e.g., JAN, FEB, NOV), it remains unchanged. If a year is present, always convert it to a full four-digit format without spaces. If the year is in two-digit format (e.g., 24, 20), expand it to its correct four-digit representation (e.g., DEC-24 ? DEC-2024, JANUARY-20 ? JAN-2020, MAR-20 ? MAR-2020, OCT'24 ? OCT-2024, OCT 25 ? OCT-2025). The output should strictly follow the format MMM-YYYY when a year is included.
           - If no valid period of service is found, return None, Do not give period of service other than this format MMM-YYYY.
           - If 'Particulars' or 'Description' appears as a heading, extract the first line of the corresponding content below it as the description for 'Description of Services For the Month Of'.
           - Extract MSME codes properly and put value under the 'MSME Code' key.
           - Extract Dealer code properly from the document, (if e.g DEALERCODEW3224 then dealer code is W3224)
           - Extract values for the following keys and provide them in the specified format. If any key is missing or has no value, set it as null:
           - Extract Quantity (look for headers like 'Quantity', 'Qty', 'QTY', 'Qnty'). If found in table or description, extract the numerical integer value (e.g., 1). No text in this field.
           - Make sure proper invoice number extract from the invoice.
           - Extract Proper Bank Name only (Put actual Bank Name inside key) and put it under the 'Bank Name' key (e.g., if you see "Bank Name : Indian Bank", extract "Indian Bank"). If it's without spaces then add space where needed.
           - Extract the Invoice Reference Number (IRN) properly without missing anything. The IRN is always a 64-character hexadecimal string (containing only 0-9 and a-f). If the IRN is split across two lines with a hyphen ('-'), remove the hyphen and merge both parts to reconstruct the full 64-character IRN. Ensure that the extracted IRN is exactly 64 characters long and does not contain any extra or missing characters. and put this inside 'IRN' key.
           - **IRN (Invoice Reference Number)**: 
             - Extract the IRN exactly as follows:
               - The IRN is a 64-character hexadecimal string containing only digits (0-9) and lowercase letters (a-f).
               - If the IRN is split across two lines with a hyphen ('-'), remove the hyphen and join the parts.
               - Do not include any extra characters, spaces, punctuation, or newlines. The final output must be trimmed so that it is exactly 64 characters long.
               - Also strictly do not add anything extra characters like digits and letters and lenght should be 64 including digits and letters only.
               - If the resulting IRN is not exactly 64 characters, consider it invalid and return null for this key.
           - Service Provider State / Supplier's Place of Supply: Extract the state from the address of supplier or service provider if mentioned, and assign it to this key.
           - Service Provider State / Supplier's Place of Supply sometimes mentioned in address as well that state you need to fetch and put it under Service Provider State / Supplier's Place of Supply key"
           - Extract the address and place of supply only from the invoice bill, not from the Turnover Declaration Letter.
             - Document Type
             - IRN
             - Ack No
             - Ack Date
             - Invoice No
             - Invoice Date
             - Taxable Value
             - CGST Amount
             - SGST / UTGST Amount
             - IGST Amount
             - Total Invoice Value
             - Dealer Code
             - HIIB-MISP CODE
             - A/c Holder's Name
             - Bank Name
             - A/c No
             - Branch
             - Bank IFSC
             - MICR Code
             - HIIB GSTIN / Customer GSTIN
             - HIIB PINCODE / Customer PINCODE
             - Dealer PINCODE
             - Dealer GSTIN
             - HIIB State Code 
             - Dealer State Code 
             - IsMSME
             - MSME Code
             - Dealer PAN / PAN
             - SAC
             - Service Provider Detail
             - Service Provider Address
             - Service Provider Pincode
             - Billed To Detail
             - Billed To Address (Strictly preserve all original punctuation marks like commas and hyphens exactly as they appear in the document)
             - Billed To Pincode
             - Service Provider State / Supplier's Place of Supply
             - Billed To State / Recipient's Place of Supply
             - Description of Services For the Month Of
             - OEM
             - Quantity
             - PERIOD OF SERVICE
             - TELEPHONE NUMBER
             

            The format should be as follows:

            "form": {
                "IRN": "value1",
                "Ack No": "value2",
                "Ack Date": "dd/mm/yyyy",
                "Invoice No": "value3",
                ...
            }

        2. **General Rules**:
           - Only return the structured JSON with the extracted data, no extra text.
           - Ensure no extra colons or commas.
           - If bank details are in one line, extract and assign each value correctly. Ensure bank_name contains only the bank's name and account_no contains only the account number (e.g., if line has Bank Name A/C No., keep them separate in relevant keys).
           - If "Branch & IFS Code" appears, consider the first part as the branch and the second part as the branch IFSC. For Bank IFSC codes: The first 4 characters are strictly letters, the 5th character is ALWAYS the number '0' (zero), not 'o' or 'O'. The last 6 characters can be alphanumeric, BUT the letter 'O' is virtually NEVER used in the last 6 characters to avoid confusion with zero. If the character looks like an 'O', it is almost certainly a 'C' or a '0'. Look extremely closely at the curve to distinguish 'C' from '0'.
           - If the IFSC contains a prefix (e.g., "GKP-HDFC0000284"), extract only the valid IFSC part (e.g., "HDFC0000284") while assigning the prefix (e.g., "GKP") to the branch, ensuring all variations follow the same pattern by separating the branch and IFSC correctly without merging them.
           - If the GSTIN contains a prefix or suffix remove that prefix and suffix just give proper GSTIN part only.
           - For any GSTIN (like HIIB GSTIN or Dealer GSTIN), strictly follow the Indian GSTIN format: 2 Digits, 5 Letters, 4 Digits, 1 Letter, 1 Digit, 1 Letter, 1 Alphanumeric character. Ensure there is no confusion between the letter 'O' and number '0', or letter 'I' and number '1' based on this strict positional format.
           - Dynamically extract GSTIN near labels like 'Billing to', 'Billed to', or similar as hiib_gstin, and GSTIN near issuer header (top section or near company name) as dealer_gstin. Use nearby context like 'GST', 'GSTIN', or location cues to assign correctly.
           - HIIB GSTIN and dealer GSTIN is not same, extract properly and assign accordingly.
           - If document is blank or nothing, then give key with null value, no additional text other than requested format.
           - If OEM is not defined then put value as null, not any random.
           - For HDFC Bank and Bank of baroda (BOB) Ensure the extracted account number is exactly 14 digits long, If SBI(State bank of india) then 17 digits long, kindly check zeros on it, do not add extra. If it is not, return null.
           - Dealer PAN / PAN is the company's PAN, not Hyundai (HIIB)'s PAN. If multiple PANs are present, exclude Hyundai's (HIIB) PAN and take the other one. If only Hyundai's PAN is found or no other PAN is available, return null. Do not consider Hyundai or HIIB PAN as the dealer PAN.           
           - Do not consider TAN No as PAN No, both are different.
           - In some cases, the Dealer Code follows the format A1234. If it matches this format, it must be strictly followed, (remove -, _ if has in between).
           - Extract Ack No. (Acknowledgement No) properly without missing or adding extract character, strickly follows rules, make sure it is of 15 character not fixed all Acknowledgement are 15 character.
           - Ensure that the Service Provider State (Supplier's Place of Supply) and the Billed To State (Recipient's Place of Supply) are correctly extracted from the relevant addresses. Do not infer them from "Place of Supply.". Remove any codes (e.g., (06), (new)) or extra text inside parentheses.
           - If a state has a code in parentheses, use it as the State Code (e.g., Haryana (06) → Place of Supply: Haryana, State Code: 06). Ignore non-numeric text in parentheses (e.g., "(new)"). Extract Place of Supply strictly from the relevant address.
           - Extract Service Provider State (Supplier's Place of Supply) and Billed To State (Recipient's Place of Supply)  strictly from the relevant address state. 
           - Extract telephone number properly if available else add null.
           - If Hyundai exist then it is buyer so place details inside buyer and other one is service provider.
           
        3. **Dedicated IRN Extraction Mode (if required)**:
            - When re-extracting only the IRN (for example, when the initially extracted IRN is not exactly 64 characters), output JSON containing only the IRN key.
            - In this mode, ensure that the IRN is extracted strictly as a 64-character hexadecimal string (only digits 0-9 and lowercase letters a-f).
            - If the IRN is not exactly 64 characters, return null for the IRN key.
            
        4. **Date Extraction Rule**:
            - Date should be in dd/mm/yyyy format.
            - POSITION-BASED EXTRACTION: Always treat positions as Day/Month/Year(Day-Month-Year) regardless of number values.
            - Strict Order: Day = first, Month = middle, Year = last. Never swap positions. (e.g., 20-06-25 MUST become 20/06/2025 (NEVER 25/06/2020)).
            
        - Analyze text properly do not add or miss any one character from the value, stricky check irn number and account number properly (If HDFC bank is there then 14 digit account number is there).
        - Analyze the IRN number strictly to ensure it contains exactly 64 characters. It must be a valid hexadecimal string consisting only of lowercase lettersand digit. Do not include any extra characters, spaces, or formatting errors. If the IRN is split across two lines with a hyphen, remove only the hyphen and join the two parts to reconstruct the full 64 character IRN. Do not modify, add, or remove any characters other than the hyphen if present. Ensure the extracted IRN is exactly 64 characters long no more, no less.
        The goal is to extract only the keys listed above with their values, ensuring proper formatting, and exclude empty or missing fields, if page is blank or no content on it then return key with null value in given format only without any addtional information.
        """

        self.USER_PROMPT = "Extract given things from the image."


    def zoom_and_split_image(self, image_bytes):
        """
        Zooms in on the image and splits it into four parts for better readability.

        Args:
            image_bytes (bytes): The image data in bytes.

        Returns:
            tuple: Four base64-encoded strings of the zoomed and split images.
        """
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode == "RGBA":
            image = image.convert("RGB")
        # original_image_bytes = io.BytesIO()
        # image.save(original_image_bytes, format="JPEG")
        # original_image_base64 = base64.b64encode(original_image_bytes.getvalue()).decode('utf-8')
        logger(level="INFO", status_code=200, message=f"Original image dimensions: {image.width}x{image.height}", endpoint="zoom_and_split_image")
        image = rotate_and_enhance_image_for_ocr(image)
        zoomed_image = image.resize((int(image.width * 1.5), int(image.height * 1.5)))
        
        logger(level="INFO", status_code=200, message=f"Zoomed image dimensions: {zoomed_image.width}x{zoomed_image.height}", endpoint="zoom_and_split_image")
        max_size = 8000

        width, height = zoomed_image.size
        part_height = height // 4  # Split into 4 equal parts
        if width > max_size or height > max_size:
            scale_factor = min(max_size / width, max_size / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            zoomed_image = zoomed_image.resize((new_width, new_height))
            logger(level="INFO", status_code=200, message=f"Resized image dimensions: {zoomed_image.width}x{zoomed_image.height}", endpoint="zoom_and_split_image")
            
        width, height = zoomed_image.size
        part_height = height // 4
    
        # Crop the image into 4 parts
        upper_image = zoomed_image.crop((0, 0, width, part_height))
        upper_middle_image = zoomed_image.crop((0, part_height, width, part_height * 2))
        lower_middle_image = zoomed_image.crop((0, part_height * 2, width, part_height * 3))
        lower_image = zoomed_image.crop((0, part_height * 3, width, height))

        upper_half_image = zoomed_image.crop((0, 0, width, part_height * 2))
         # Save images locally for verification
        # upper_image.save("upper_image.jpg", "JPEG")
        # upper_middle_image.save("upper_middle_image.jpg", "JPEG")
        # lower_middle_image.save("lower_middle_image.jpg", "JPEG")
        # lower_image.save("lower_image.jpg", "JPEG")
        # upper_half_image.save("upper_half_image.jpg", "JPEG")


        # Convert images to bytes
        upper_image_bytes = io.BytesIO()
        upper_middle_image_bytes = io.BytesIO()
        lower_middle_image_bytes = io.BytesIO()
        lower_image_bytes = io.BytesIO()
        upper_half_image_bytes = io.BytesIO()

        upper_image.save(upper_image_bytes, format="JPEG")
        upper_middle_image.save(upper_middle_image_bytes, format="JPEG")
        lower_middle_image.save(lower_middle_image_bytes, format="JPEG")
        lower_image.save(lower_image_bytes, format="JPEG")
        upper_half_image.save(upper_half_image_bytes, format="JPEG")

        # Encode images in Base64
        upper_image_base64 = base64.b64encode(upper_image_bytes.getvalue()).decode('utf-8')
        upper_middle_image_base64 = base64.b64encode(upper_middle_image_bytes.getvalue()).decode('utf-8')
        lower_middle_image_base64 = base64.b64encode(lower_middle_image_bytes.getvalue()).decode('utf-8')
        lower_image_base64 = base64.b64encode(lower_image_bytes.getvalue()).decode('utf-8')
        upper_half_image_base64 = base64.b64encode(upper_half_image_bytes.getvalue()).decode('utf-8')


        return upper_image_base64, upper_middle_image_base64, lower_middle_image_base64, lower_image_base64, upper_half_image_base64

    @staticmethod
    def encode_image_to_base64(image_bytes):
        """
        Encodes image bytes to a base64 string.

        Args:
            image_bytes (bytes): The image data in bytes.

        Returns:
            str: The base64-encoded string of the image.
        """
        return base64.b64encode(image_bytes).decode('utf-8')

    @staticmethod
    def map_invoice_data(response_text):
        """
        Maps the given JSON response text to a dictionary with specified keys, 
        validates certain fields, and updates the dictionary with the validation results.
        
        Args:
        - response_text (str): The raw JSON response as a string.
        
        Returns:
        - dict: A dictionary with the mapped and validated key-value pairs.
        """
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            try:
                # Attempt to clean single quotes, None, True, False
                cleaned = re.sub(r"'", '"', response_text)
                cleaned = re.sub(r'\bNone\b', 'null', cleaned)
                cleaned = re.sub(r'\bTrue\b', 'true', cleaned)
                cleaned = re.sub(r'\bFalse\b', 'false', cleaned)
                data = json.loads(cleaned)
            except Exception:
                return None

        # def validate_gstin(gstin):
        #     """Validate GSTIN format (15 characters, specific format)."""
        #     return bool(re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", gstin))

        def upper_case(text):
            """Validate PAN format (10 characters, specific format)."""
            return text.upper() if text else None

        def fix_ifsc(ifsc) -> str:
            if not ifsc or not isinstance(ifsc, str):
                return ifsc
            ifsc = upper_case(ifsc)
            
            # The 5th character is ALWAYS '0'
            if len(ifsc) > 4 and ifsc[4] == 'O':
                ifsc = ifsc[:4] + '0' + ifsc[5:]
                
            # For the last 6 characters, 'O' is virtually never used (to avoid confusion with zero)
            if len(ifsc) > 5:
                ifsc = ifsc[:5] + ifsc[5:].replace('O', '0')
                
            return ifsc

        def clean_gstin(gstin: str) -> str:
            if not gstin:
                return gstin
            for sep in ['-', '_', ' ']:
                if sep in gstin:
                    gstin = gstin.split(sep)[0]
                    break
            gstin = upper_case(gstin.strip())
            
            # Programmatically fix common OCR mistakes in 15-char GSTINs
            if len(gstin) == 15:
                gstin_list = list(gstin)
                digit_indices = [0, 1, 7, 8, 9, 10, 12]
                letter_indices = [2, 3, 4, 5, 6, 11, 13]
                
                for idx in digit_indices:
                    if gstin_list[idx] == 'O': gstin_list[idx] = '0'
                    elif gstin_list[idx] == 'I': gstin_list[idx] = '1'
                    elif gstin_list[idx] == 'S': gstin_list[idx] = '5'
                    elif gstin_list[idx] == 'B': gstin_list[idx] = '8'
                    elif gstin_list[idx] == 'Z': gstin_list[idx] = '2'
                
                for idx in letter_indices:
                    if gstin_list[idx] == '0': gstin_list[idx] = 'O'
                    elif gstin_list[idx] == '1': gstin_list[idx] = 'I'
                    elif gstin_list[idx] == '5': gstin_list[idx] = 'S'
                    elif gstin_list[idx] == '8': gstin_list[idx] = 'B'
                    elif gstin_list[idx] == '2': gstin_list[idx] = 'Z'
                    
                gstin = "".join(gstin_list)
            
            return gstin
        
        form_dict = data.get("form") if (isinstance(data, dict) and "form" in data and isinstance(data["form"], dict)) else (data if isinstance(data, dict) else {})

        mapped_data = {
            "doc_type": form_dict.get("Document Type") or form_dict.get("doc_type"),
            "irn": form_dict.get("IRN") or form_dict.get("irn"),
            "ack_no": form_dict.get("Ack No") or form_dict.get("ack_no"),
            "ack_date": form_dict.get("Ack Date") or form_dict.get("ack_date"),
            "invoice_no": form_dict.get("Invoice No") or form_dict.get("invoice_no"),
            "invoice_date": form_dict.get("Invoice Date") or form_dict.get("invoice_date"),
            "taxable_value": form_dict.get("Taxable Value") or form_dict.get("taxable_value"),
            "cgst_amount": form_dict.get("CGST Amount") or form_dict.get("cgst_amount"),
            "sgst_utgst_amount": form_dict.get("SGST / UTGST Amount") or form_dict.get("sgst_utgst_amount"),
            "igst_amount": form_dict.get("IGST Amount") or form_dict.get("igst_amount"),
            "total_invoice_value": form_dict.get("Total Invoice Value") or form_dict.get("total_invoice_value"),
            "dealer_code": form_dict.get("Dealer Code") or form_dict.get("dealer_code"),
            "hiib_misp_code": form_dict.get("HIIB-MISP CODE") or form_dict.get("hiib_misp_code"),
            "account_holders_name": form_dict.get("A/c Holder's Name") or form_dict.get("account_holders_name"),
            "bank_name": form_dict.get("Bank Name") or form_dict.get("bank_name"),
            "account_no": form_dict.get("A/c No") or form_dict.get("account_no"),
            "branch": form_dict.get("Branch") or form_dict.get("branch"),
            "bank_ifsc": form_dict.get("Bank IFSC") or form_dict.get("bank_ifsc"),
            "micr_code": form_dict.get("MICR Code") or form_dict.get("micr_code"),
            "hiib_gstin": clean_gstin(form_dict.get("HIIB GSTIN / Customer GSTIN") or form_dict.get("hiib_gstin")),
            "dealer_gstin": clean_gstin(form_dict.get("Dealer GSTIN") or form_dict.get("dealer_gstin")),
            "hiib_pincode": form_dict.get("HIIB PINCODE / Customer PINCODE") or form_dict.get("hiib_pincode"),
            "dealer_pincode": form_dict.get("Dealer PINCODE") or form_dict.get("dealer_pincode"),
            "hiib_state_code": form_dict.get("HIIB State Code") or form_dict.get("hiib_state_code"),
            "dealer_state_code": form_dict.get("Dealer State Code") or form_dict.get("dealer_state_code"),
            "ismsme": form_dict.get("IsMSME") or form_dict.get("ismsme"),
            "msme_code": form_dict.get("MSME Code") or form_dict.get("msme_code"),
            "dealer_pan": upper_case(form_dict.get("Dealer PAN / PAN") or form_dict.get("dealer_pan")),
            "sac": form_dict.get("SAC") or form_dict.get("sac"),
            "consigner_details": form_dict.get("Service Provider Detail") or form_dict.get("consigner_details"),
            "consigner_address": form_dict.get("Service Provider Address") or form_dict.get("consigner_address"),
            "consigner_pincode": form_dict.get("Service Provider Pincode") or form_dict.get("consigner_pincode"),
            "buyer_name": form_dict.get("Billed To Detail") or form_dict.get("buyer_name"),
            "buyer_address": form_dict.get("Billed To Address") or form_dict.get("buyer_address"),
            "buyer_pincode": form_dict.get("Billed To Pincode") or form_dict.get("buyer_pincode"),
            "consigner_place_of_supply": form_dict.get("Service Provider State / Supplier's Place of Supply") or form_dict.get("consigner_place_of_supply"),
            "buyer_place_of_supply": form_dict.get("Billed To State / Recipient's Place of Supply") or form_dict.get("buyer_place_of_supply"),
            "description_of_service": form_dict.get("Description of Services For the Month Of") or form_dict.get("description_of_service"),
            "oem": form_dict.get("OEM") or form_dict.get("oem"),
            "quantity": None,
            "period_of_service": form_dict.get("PERIOD OF SERVICE") or form_dict.get("period_of_service"),
            "telephone_number": form_dict.get("TELEPHONE NUMBER") or form_dict.get("telephone_number")
        }

        qty_val = None
        for qk in ["Quantity", "Qty", "QTY", "qty", "quantity", "ItemCnt"]:
            v = form_dict.get(qk)
            if v not in [None, "", []]:
                qty_val = str(v)
                break
        mapped_data["quantity"] = qty_val

        msme_code_value = mapped_data.get("msme_code", "")
        if msme_code_value and "MSME" in msme_code_value:
            msme_code_value = msme_code_value.replace("MSME", "").replace("msme", "").strip()
            mapped_data["msme_code"] = msme_code_value if msme_code_value else None

        period_of_service=mapped_data.get("period_of_service", "")
        if period_of_service:
            period_of_service_value = format_month_year(period_of_service)
            mapped_data["period_of_service"] = period_of_service_value if period_of_service_value else None

        bank_name=mapped_data.get("bank_name", "")
        if bank_name and ("HDFC" in bank_name.upper() or "hdfc" in bank_name.lower()):
            bank_name_value = rearrange_bank_name(bank_name)
            mapped_data["bank_name"] = bank_name_value if bank_name_value else None

        bank_ifsc = mapped_data.get("bank_ifsc", "")
        if bank_ifsc:
            mapped_data["bank_ifsc"] = fix_ifsc(bank_ifsc)
    
        consigner_address=mapped_data.get("consigner_address", "")
        refactored_consigner_address = remove_repeating_address(consigner_address, min_words=3, max_words=5)
        mapped_data["consigner_address"] =  refactored_consigner_address if refactored_consigner_address else None

        buyer_address=mapped_data.get("buyer_address", "")
        refactored_buyer_address = remove_repeating_address(buyer_address, min_words=3, max_words=5)
        mapped_data["buyer_address"] =  refactored_buyer_address if refactored_buyer_address else None

        # if mapped_data["dealer_gstin"] and not validate_gstin(mapped_data["dealer_gstin"]):
        #     mapped_data["dealer_gstin"] = "INVALID"
        
        # if mapped_data["hiib_gstin"] and not validate_gstin(mapped_data["hiib_gstin"]):
        #     mapped_data["hiib_gstin"] = "INVALID"

        # if mapped_data["dealer_pan"] and not validate_pan(mapped_data["dealer_pan"]):
        #     mapped_data["dealer_pan"] = "INVALID"

        return {"form": mapped_data}

    def generate_response(self, image_bytes):
        """
        Generate a response from an external LLM when configured, otherwise use the local fallback.

        Args:
            image_bytes (bytes): The image data in bytes.

        Returns:
            dict: A structured JSON response from the configured provider or a local fallback.
        """
        try:
            if self.use_external_llm:
                if self.external_llm_provider in ("groq", "grok"):
                    try:
                        import openai
                    except ImportError:
                        logger(level="WARNING", status_code=200, message="OpenAI package is not installed; falling back to local mode.", endpoint="generate_response")
                        self.use_external_llm = False

                    if self.use_external_llm:
                        try:
                            base_url = self.external_llm_base_url or "https://api.groq.com/openai/v1"
                            client = openai.OpenAI(api_key=self.external_llm_api_key, base_url=base_url)
                            
                            is_vision_model = any(keyword in self.external_llm_model.lower() for keyword in ("vision", "llama-3.2"))
                            
                            if is_vision_model:
                                response = client.chat.completions.create(
                                    model=self.external_llm_model,
                                    messages=[
                                        {"role": "system", "content": self.SYSTEM_PROMPT},
                                        {"role": "user", "content": [
                                            {"type": "text", "text": "Extract info from this document"},
                                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"}}
                                        ]}
                                    ],
                                )
                            else:
                                import easyocr
                                ocr_reader = easyocr.Reader(['en'], gpu=False)
                                nparr = np.frombuffer(image_bytes, np.uint8)
                                image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                ocr_results = ocr_reader.readtext(image_cv, detail=0)
                                ocr_text = " ".join(ocr_results)
                                
                                response = client.chat.completions.create(
                                    model=self.external_llm_model,
                                    messages=[
                                        {"role": "system", "content": self.SYSTEM_PROMPT},
                                        {"role": "user", "content": f"Here is the OCR text of the document. Extract the structured fields from it: {ocr_text}"}
                                    ],
                                )
                            
                            response_text = response.choices[0].message.content
                            prompt_tokens = getattr(response.usage, "prompt_tokens", None) if hasattr(response, "usage") else None
                            completion_tokens = getattr(response.usage, "completion_tokens", None) if hasattr(response, "usage") else None
                            
                            try:
                                json.loads(response_text)
                            except json.JSONDecodeError:
                                start_idx = response_text.find('{')
                                end_idx = response_text.rfind('}')
                                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                                    response_text = response_text[start_idx:end_idx+1]
                                
                            mapped_data = self.map_invoice_data(response_text)
                            if mapped_data:
                                return mapped_data, prompt_tokens, completion_tokens
                        except Exception as provider_error:
                            logger(level="WARNING", status_code=200, message=f"External LLM request failed for Groq/Grok: {provider_error}; falling back to local mode.", endpoint="generate_response")

                elif self.external_llm_provider == "gemini":
                    try:
                        import google.generativeai as genai
                    except ImportError:
                        logger(level="WARNING", status_code=200, message="google-generativeai is not installed; falling back to local mode.", endpoint="generate_response")

                    if self.use_external_llm:
                        try:
                            genai.configure(api_key=self.external_llm_api_key)
                            model = genai.GenerativeModel(self.external_llm_model)
                            image = Image.open(io.BytesIO(image_bytes))
                            if image.mode != "RGB":
                                image = image.convert("RGB")
                            image_bytes_for_prompt = io.BytesIO()
                            image.save(image_bytes_for_prompt, format="PNG")
                            response = model.generate_content(
                                [
                                    self.SYSTEM_PROMPT,
                                    image,
                                    self.USER_PROMPT,
                                ]
                            )
                            response_text = response.text
                            usage_meta = getattr(response, "usage_metadata", None)
                            prompt_tokens = getattr(usage_meta, "prompt_token_count", None) if usage_meta else None
                            completion_tokens = getattr(usage_meta, "candidates_token_count", None) if usage_meta else None
                            mapped_data = self.map_invoice_data(response_text)
                            if mapped_data:
                                return mapped_data, prompt_tokens, completion_tokens
                        except Exception as provider_error:
                            logger(level="WARNING", status_code=200, message=f"External LLM request failed for Gemini: {provider_error}; falling back to local mode.", endpoint="generate_response")

            fallback_json = json.dumps({
                "form": {
                    "Document Type": None,
                    "IRN": None,
                    "Ack No": None,
                    "Ack Date": None,
                    "Invoice No": None,
                    "Invoice Date": None,
                    "Taxable Value": None,
                    "CGST Amount": None,
                    "SGST / UTGST Amount": None,
                    "IGST Amount": None,
                    "Total Invoice Value": None,
                    "Dealer Code": None,
                    "HIIB-MISP CODE": None,
                    "A/c Holder's Name": None,
                    "Bank Name": None,
                    "A/c No": None,
                    "Branch": None,
                    "Bank IFSC": None,
                    "MICR Code": None,
                    "HIIB GSTIN / Customer GSTIN": None,
                    "HIIB PINCODE / Customer PINCODE": None,
                    "Dealer PINCODE": None,
                    "Dealer GSTIN": None,
                    "HIIB State Code": None,
                    "Dealer State Code": None,
                    "IsMSME": None,
                    "MSME Code": None,
                    "Dealer PAN / PAN": None,
                    "SAC": None,
                    "Service Provider Detail": None,
                    "Service Provider Address": None,
                    "Service Provider Pincode": None,
                    "Billed To Detail": None,
                    "Billed To Address": None,
                    "Billed To Pincode": None,
                    "Service Provider State / Supplier's Place of Supply": None,
                    "Billed To State / Recipient's Place of Supply": None,
                    "Description of Services For the Month Of": None,
                    "OEM": None,
                    "Quantity": None,
                    "PERIOD OF SERVICE": None,
                    "TELEPHONE NUMBER": None
                }
            })
            mapped_fallback = self.map_invoice_data(fallback_json)
            mapped_fallback["_local_fallback"] = True
            return mapped_fallback, None, None

        except Exception as e:
            logger(level="WARNING", status_code=200, message=f"Unexpected error during LLM generation; returning local fallback: {e}", endpoint="generate_response")
            fallback_json = json.dumps({
                "form": {
                    "Document Type": None,
                    "IRN": None,
                    "Ack No": None,
                    "Ack Date": None,
                    "Invoice No": None,
                    "Invoice Date": None,
                    "Taxable Value": None,
                    "CGST Amount": None,
                    "SGST / UTGST Amount": None,
                    "IGST Amount": None,
                    "Total Invoice Value": None,
                    "Dealer Code": None,
                    "HIIB-MISP CODE": None,
                    "A/c Holder's Name": None,
                    "Bank Name": None,
                    "A/c No": None,
                    "Branch": None,
                    "Bank IFSC": None,
                    "MICR Code": None,
                    "HIIB GSTIN / Customer GSTIN": None,
                    "HIIB PINCODE / Customer PINCODE": None,
                    "Dealer PINCODE": None,
                    "Dealer GSTIN": None,
                    "HIIB State Code": None,
                    "Dealer State Code": None,
                    "IsMSME": None,
                    "MSME Code": None,
                    "Dealer PAN / PAN": None,
                    "SAC": None,
                    "Service Provider Detail": None,
                    "Service Provider Address": None,
                    "Service Provider Pincode": None,
                    "Billed To Detail": None,
                    "Billed To Address": None,
                    "Billed To Pincode": None,
                    "Service Provider State / Supplier's Place of Supply": None,
                    "Billed To State / Recipient's Place of Supply": None,
                    "Description of Services For the Month Of": None,
                    "OEM": None,
                    "Quantity": None,
                    "PERIOD OF SERVICE": None,
                    "TELEPHONE NUMBER": None
                }
            })
            mapped_fallback = self.map_invoice_data(fallback_json)
            mapped_fallback["_local_fallback"] = True
            return mapped_fallback, None, None

    def qr_extract(self, image, page_index):
        """
        Extract and process QR codes from an image, page-wise, returning their base64 data in a list.
        
        Args:
            image: Input image containing QR codes.
            page_index: Index of the page being processed.

        Returns:
            A list of decoded QR code data as strings.
        """
        logger(level='INFO', status_code=200, message=f"Processing page {page_index}...", endpoint='qr_extract')

        decoded_qr_data = []

        try:
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            screen_width, screen_height = 800, 800
            height, width, _ = image.shape
            if width > screen_width or height > screen_height:
                scaling_factor = min(screen_width / width, screen_height / height)
                resized_image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

            decoded_texts, _ = self.qreader.detect_and_decode(image=image, return_detections=True)
            decoded_qr_data = [qr_text.strip() for qr_text in decoded_texts if qr_text]
            logger(level='INFO', status_code=200, message=f"Decoded QR codes: {decoded_qr_data}", endpoint='qr_extract')

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"Error processing QR codes: {e}"
            handle_error(error_type,"qr_extract",error_msg)

        return decoded_qr_data

    def form_extract_llm(self, image_bytes, page, i):
        """
        Extract structured data from a document using the LLM.

        Args:
            image_bytes (bytes): The image data in bytes.
            page (int): Page number for QR extraction.
            i (int): Some identifier for processing.

        Returns:
            dict: The extracted form data.
        """
        try:
            max_retries = 1
            last_valid_form = {}
            for attempt in range(1, max_retries + 1):
                response, input_tokens, output_tokens = self.generate_response(image_bytes)
                form = response.get('form', {})
                irn = form.get("irn", "")
                
                logger(level="INFO", status_code=200, message=f"IRN Value : {irn}..", endpoint="form_extract_llm")
                if response.get("_local_fallback"):
                    logger(level="INFO", status_code=200, message="Returning local fallback form without QR extraction.", endpoint="form_extract_llm")
                    return {"form": form}, input_tokens, output_tokens

                if irn:
                    last_valid_form = form
                
                if not irn:
                    qr_data = self.qr_extract(page, i)
                    form["qr_value"] = qr_data
                    logger(level="INFO", status_code=200, message="Form extraction completed with NUll IRN.", endpoint="form_extract_llm")
                    return {"form": form}, input_tokens, output_tokens
                
                if len(irn) == 64:
                    qr_data = self.qr_extract(page, i)
                    form["qr_value"] = qr_data
                    logger(level="INFO", status_code=200, message="Form extraction completed with valid IRN.", endpoint="form_extract_llm")
                    return {"form": form}, input_tokens, output_tokens

                logger(level="WARNING", status_code=400, message=f"Invalid IRN length ({len(irn)}). Retrying... ({attempt}/{max_retries})", endpoint="form_extract_llm")

            logger(level="ERROR", status_code=500, message="Failed to obtain valid IRN after 3 attempts. Proceeding with last available data.", endpoint="form_extract_llm")
            qr_data = self.qr_extract(page, i)
            last_valid_form["qr_value"] = qr_data
            return {"form": last_valid_form}, input_tokens, output_tokens

        except Exception as e:
            error_type = "exception_error"
            error_msg = f"An error occurred during form extraction: {e}"
            handle_error(error_type, "form_extract_llm", error_msg)

document_llm_service = DocumentLLMService()