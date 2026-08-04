import io
import os
import unittest
from PIL import Image
import fitz
from app.jobs.job_helpers import document_processing_service

class PDFProcessingTests(unittest.TestCase):
    def test_pdf_rendering_with_fitz(self):
        # Create a simple PDF using fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test PDF Content")
        
        pdf_bytes = doc.write()
        doc.close()
        
        # Save to temp file
        temp_pdf = os.path.join(os.getcwd(), "temp_test_render.pdf")
        with open(temp_pdf, "wb") as f:
            f.write(pdf_bytes)
            
        try:
            # Let's count pages
            count = document_processing_service.get_pdf_page_count(temp_pdf, temp_pdf)
            self.assertEqual(count, 1)
            
            # Let's test the PyMuPDF rendering inside extract_data pathway
            doc_fitz = fitz.open(temp_pdf)
            pages = []
            for page_num in range(len(doc_fitz)):
                p = doc_fitz.load_page(page_num)
                pix = p.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                pages.append(pil_img)
            doc_fitz.close()
            
            self.assertEqual(len(pages), 1)
            self.assertIsInstance(pages[0], Image.Image)
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

if __name__ == "__main__":
    unittest.main()
