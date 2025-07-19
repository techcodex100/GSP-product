import os
import time
import datetime
import requests
import psutil
from faker import Faker
from pydantic import BaseModel

fake = Faker()

# Output directory
pdf_output_dir = "rendered_gsp_pdfs"
os.makedirs(pdf_output_dir, exist_ok=True)

# Render API URL
RENDER_URL = "https://gsp-product.onrender.com/generate-gsp-certificate-pdf/"

# Max retries for failed requests
MAX_RETRIES = 5
DELAY_BETWEEN_REQUESTS = 2  # seconds

class GSPCertificateData(BaseModel):
    reference_no: str
    issued_in: str
    consigned_from: str
    consigned_to: str
    transport_route: str
    official_use: str
    item_number: str
    package_marks: str
    package_description: str
    origin_criterion: str
    gross_weight_or_quantity: str
    invoice_number_date: str
    certification: str
    declaration: str

def generate_dummy_data():
    return GSPCertificateData(
        reference_no=fake.uuid4(),
        issued_in=fake.city(),
        consigned_from=fake.company() + "\n" + fake.address(),
        consigned_to=fake.company() + "\n" + fake.address(),
        transport_route=fake.sentence(nb_words=6),
        official_use=fake.text(max_nb_chars=100),
        item_number=str(fake.random_int(min=1, max=10)),
        package_marks=fake.lexify(text="PKG-?????"),
        package_description=fake.sentence(nb_words=8),
        origin_criterion=fake.random_letter().upper(),
        gross_weight_or_quantity=str(fake.random_int(min=100, max=1000)) + " kg",
        invoice_number_date=f"INV-{fake.random_number(digits=4)}/{fake.date()}",
        certification=fake.paragraph(nb_sentences=2),
        declaration=fake.paragraph(nb_sentences=2)
    )

# Main loop
for i in range(1, 51):  # Generate 10 PDFs
    dummy_data = generate_dummy_data()
    start_time = time.time()
    success = False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(RENDER_URL, json=dummy_data.model_dump())
            if response.status_code == 200:
                success = True
                break
            else:
                print(f"⚠️ Attempt {attempt}: Failed to generate PDF {i} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Exception: {e}")
        time.sleep(3)

    if not success:
        print(f"❌ Skipped PDF {i} after {MAX_RETRIES} retries.")
        continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = os.path.join(pdf_output_dir, f"gsp_certificate_{i}_{timestamp}.pdf")

    with open(pdf_filename, "wb") as pdf_file:
        pdf_file.write(response.content)

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    elapsed = round(time.time() - start_time, 2)

    print(f"✅ [{i}/50] PDF Generated: {pdf_filename}")
    print(f"   CPU Usage: {cpu}% | Memory: {mem}% | Time: {elapsed}s")
    print("-" * 50)

    time.sleep(DELAY_BETWEEN_REQUESTS)

print("🎉 All 50 GSP PDFs attempted with retry and delay logic.")
