from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
import os

app = FastAPI(title="GSP Certificate Generator", version="1.0.0")

@app.get("/")
def root():
    return {"message": "GSP Certificate Generator is running 🎯"}

class GSPCertificateData(BaseModel):
    reference_no: Optional[str] = ""
    issued_in: Optional[str] = ""
    consigned_from: Optional[str] = ""
    consigned_to: Optional[str] = ""
    transport_route: Optional[str] = ""
    official_use: Optional[str] = ""
    item_number: Optional[str] = ""
    package_marks: Optional[str] = ""
    package_description: Optional[str] = ""
    origin_criterion: Optional[str] = ""
    gross_weight_or_quantity: Optional[str] = ""
    invoice_number_date: Optional[str] = ""
    certification: Optional[str] = ""
    declaration: Optional[str] = ""

@app.post("/generate-gsp-certificate-pdf/")
def generate_certificate(data: GSPCertificateData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        def draw_image(filename):
            path = os.path.join(os.path.dirname(__file__), "static", filename)
            if os.path.exists(path):
                c.drawImage(ImageReader(path), 0, 0, width=width, height=height)
            else:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, 800, f"⚠️ Missing background: {filename}")

        def draw_value(value, x, y, size=12):
            c.setFont("Helvetica", size)
            for i, line in enumerate(value.splitlines()):
                c.drawString(x, y - i * size, line)

        # === Page 1 ===
        draw_image("1.jpg")

        draw_value(data.reference_no, 320, 775)
        draw_value(data.issued_in, 380, 700)
        draw_value(data.consigned_from, 60, 775)
        draw_value(data.consigned_to, 60, 710)
        draw_value(data.transport_route, 60, 630)
        draw_value(data.official_use, 310, 630)
        draw_value(data.item_number, 50, 450)
        draw_value(data.package_marks, 89, 450)
        draw_value(data.package_description, 160, 450)
        draw_value(data.origin_criterion, 375, 450)
        draw_value(data.gross_weight_or_quantity, 440, 450)
        draw_value(data.invoice_number_date, 500, 450)
        draw_value(data.certification, 60, 110)
        draw_value(data.declaration, 320, 110)

        c.showPage()
        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=gsp_certificate.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
