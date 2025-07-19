import csv
import os
import time
import datetime
import requests
import psutil
from main import GSPCertificateData  # Make sure this class matches exactly

# Render API URL
RENDER_URL = "https://gsp-product.onrender.com/generate-gsp-certificate-pdf/"

# Output directory for generated PDFs
pdf_output_dir = "gsp_pdfs_from_csv"
os.makedirs(pdf_output_dir, exist_ok=True)

# Retry POST logic
def post_with_retries(data_dict, retries=3, delay=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(RENDER_URL, json=data_dict)
            if response.status_code == 200:
                return response
            else:
                print(f"⚠️ Attempt {attempt}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt}: Exception - {str(e)}")
        time.sleep(delay)
    return None

# Load from CSV and send requests
with open("gsp_dummy_input.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        start_time = time.time()
        try:
            clean_row = {k: str(v).strip() for k, v in row.items()}
            dummy_data = GSPCertificateData(**clean_row)
        except Exception as e:
            print(f"❌ Error parsing row {idx}: {e}")
            continue

        response = post_with_retries(dummy_data.model_dump())
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = os.path.join(pdf_output_dir, f"gsp_certificate_{idx}_{timestamp}.pdf")

        if response:
            with open(pdf_filename, "wb") as f:
                f.write(response.content)
            print(f"✅ PDF Generated: {pdf_filename}")
        else:
            print(f"❌ Failed to generate PDF {idx} after retries.")

        elapsed = round(time.time() - start_time, 2)
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        print(f"   CPU: {cpu}% | MEM: {mem}% | Time: {elapsed}s")
        print("-" * 50)

        time.sleep(2)

print("🎉 All GSP Certificate PDFs generated!")
