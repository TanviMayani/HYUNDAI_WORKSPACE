import requests
import mimetypes

from dotenv import load_dotenv
from app.logging_utils import logger
from fastapi import HTTPException
from app.helpers import load_error_details, handle_error

load_dotenv()
error_details = load_error_details("error_details.json")

def msme_captcha_extraction(image_bytes):
    try:
        import easyocr
        import re
        reader = easyocr.Reader(['en'])
        
        # 1. Simple Extraction
        result = reader.readtext(image_bytes, detail=1, mag_ratio=1.5)
        if not result:
            return {"form": {"prediction": ""}}

        # 2. Basic Instruction Filter
        ignore_words = ["captcha", "type", "word", "below", "human", "enter", "characters", "prevent", "spam", "code", "image"]
        valid_items = []
        for item in result:
            if not any(word in item[1].lower() for word in ignore_words):
                valid_items.append(item)
                
        if not valid_items:
            valid_items = result
            
        # 3. Simple Height Filter (removes background noise)
        max_h = max(max(pt[1] for pt in b) - min(pt[1] for pt in b) for b, _, _ in valid_items)
        final_items = [i for i in valid_items if (max(pt[1] for pt in i[0]) - min(pt[1] for pt in i[0])) >= 0.35 * max_h]

        # 4. Sort and Combine
        final_items.sort(key=lambda item: item[0][0][0])
        detected_text = "".join([item[1] for item in final_items]).replace(" ", "")
        
        # Clean up stray instructional artifacts
        detected_text = re.sub(r'\(C\)|the', '', detected_text, flags=re.IGNORECASE)

        logger(level="INFO", status_code=200, message=f"detected_text: {detected_text}", endpoint="captcha_extract")
        return {"form": {"prediction": detected_text}}
    
    except HTTPException:
        raise   
        
    except Exception as e:
        handle_error("exception_error", "captcha_extract", f"An error occurred: {e}")