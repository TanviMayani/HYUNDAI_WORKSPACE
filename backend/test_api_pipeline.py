import time
import os
import io
import requests
import fitz

# Set up local server URL
BASE_URL = "http://127.0.0.1:8002/v1/hiib"

def create_mock_invoice_pdf():
    """Generates a mock invoice PDF for testing the LLM extraction."""
    print("Generating mock invoice PDF...")
    doc = fitz.open()
    page = doc.new_page()
    
    # Text content to simulate an invoice layout
    invoice_text = (
        "TAX INVOICE\n\n"
        "Service Provider: Alpha Services Private Limited\n"
        "Service Provider Address: Sector 15, Gurgaon, Haryana (122001)\n"
        "Dealer State Code: 06\n"
        "Dealer GSTIN: 06AAAAP9999Z1Z5\n"
        "Dealer Code: A4321\n"
        "Dealer PAN: AAAAP9999Z\n\n"
        "Billed To: Hyundai India Insurance Broking Private Limited\n"
        "Billed To Address: DLF Phase 3, Gurgaon, Haryana (122002)\n"
        "HIIB State Code: 06\n"
        "HIIB GSTIN: 06AAACH2020B1Z0\n\n"
        "Invoice Details:\n"
        "Invoice No: INV-778899\n"
        "Invoice Date: 21/07/2026\n"
        "Document Type: Tax Invoice\n\n"
        "Line Items:\n"
        "Description of Services For the Month Of: JUL-2026\n"
        "Quantity: 1\n"
        "Taxable Value: 10000.00\n"
        "CGST Amount: 900.00\n"
        "SGST / UTGST Amount: 900.00\n"
        "IGST Amount: 0.00\n"
        "Total Invoice Value: 11800.00\n\n"
        "Bank Details:\n"
        "A/c Holder's Name: Alpha Services\n"
        "Bank Name: HDFC Bank\n"
        "A/c No: 50100203040506\n"
        "Branch: Gurgaon Main\n"
        "Bank IFSC: HDFC0000284"
    )
    
    page.insert_text((50, 50), invoice_text, fontsize=11)
    pdf_bytes = doc.write()
    doc.close()
    
    buf = io.BytesIO(pdf_bytes)
    return buf

def run_pipeline():
    # 1. Create Mock Invoice file
    invoice_file = create_mock_invoice_pdf()

    # 2. Sign Up User
    signup_url = f"{BASE_URL}/signup"
    signup_payload = {
        "first_name": "Test",
        "last_name": "Runner",
        "email": "test_runner@hiib.in",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    print(f"\n1. Registering user '{signup_payload['email']}'...")
    resp = requests.post(signup_url, json=signup_payload)
    if resp.status_code == 201 or (resp.status_code == 409 and "already registered" in resp.text.lower()):
        print("-> User registered successfully (or already exists)")
    else:
        print(f"-> Registration failed: {resp.status_code} - {resp.text}")
        return

    # 3. Login to get JWT Token
    login_url = f"{BASE_URL}/login"
    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"]
    }
    print("\n2. Logging in...")
    resp = requests.post(login_url, json=login_payload)
    if resp.status_code == 200:
        token = resp.json()["detail"][0]["data"]["token"]
        print("-> Login successful. JWT token received.")
    else:
        print(f"-> Login failed: {resp.status_code} - {resp.text}")
        return

    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Generate API Key
    create_key_url = f"{BASE_URL}/create_api_key"
    print("\n3. Generating API Key using JWT Token...")
    resp = requests.post(create_key_url, headers=auth_headers)
    if resp.status_code == 201 or resp.status_code == 200:
        api_key = resp.json()["detail"][0]["data"]["api_key"]
        print(f"-> API Key generated: {api_key}")
    else:
        print(f"-> Failed to generate API key: {resp.status_code} - {resp.text}")
        return

    # From here on, use API key auth header
    api_headers = {"x-api-key": api_key}

    # 5. Get Extraction Methods List
    methods_url = f"{BASE_URL}/job/method/"
    print("\n4. Fetching method list using API key...")
    resp = requests.get(methods_url, headers=api_headers)
    if resp.status_code == 200:
        methods = resp.json()["detail"][0]["data"]
        llm_method_id = None
        for m in methods:
            if "LLM" in m["display_name"]:
                llm_method_id = m["id"]
                print(f"-> Found LLM Method ID: {llm_method_id}")
                break
        if not llm_method_id:
            print("-> Could not find 'LLM Extraction' method in database.")
            return
    else:
        print(f"-> Failed to fetch method list: {resp.status_code} - {resp.text}")
        return

    # 6. Create Invoice Job (Upload generated file)
    invoice_job_url = f"{BASE_URL}/job/invoice"
    form_data = {
        "job_name": "Integration_Test_Invoice",
        "method_id": llm_method_id
    }
    files = {
        "file": ("invoice.pdf", invoice_file, "application/pdf")
    }
    print("\n5. Submitting Invoice Extraction Job...")
    resp = requests.post(invoice_job_url, headers=api_headers, data=form_data, files=files)
    if resp.status_code == 201:
        job_id = resp.json()["detail"][0]["data"]["job_id"]
        print(f"-> Job successfully created! Job ID: {job_id}")
    else:
        print(f"-> Failed to submit job: {resp.status_code} - {resp.text}")
        return

    # 7. Poll Job Status
    job_status_url = f"{BASE_URL}/job/{job_id}"
    print(f"\n6. Polling job status for {job_id}...")
    for attempt in range(15):
        time.sleep(3)
        resp = requests.get(job_status_url, headers=api_headers)
        if resp.status_code == 200:
            job_data = resp.json()["detail"][0]["data"][0]
            status = job_data["status"]
            print(f"Attempt {attempt + 1}: Status = {status}")
            if status == "Completed":
                print("-> Job Completed successfully!")
                print("\n=== EXTRACTION RESULTS ===")
                import json
                print(json.dumps(job_data["source"][0]["result"], indent=2))
                return
            elif status == "Failed":
                print("-> Job Failed in background worker.")
                return
        else:
            print(f"-> Failed to fetch job status: {resp.status_code} - {resp.text}")
            return
    print("-> Polling timed out. The job is still in progress.")

if __name__ == "__main__":
    run_pipeline()
