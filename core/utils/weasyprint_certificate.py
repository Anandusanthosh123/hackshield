import os
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML


def generate_certificate_pdf(certificate):
    """
    Generates and saves a PDF file for a certificate (safe + idempotent).
    """

    # ✅ Do NOT regenerate if already exists
    if certificate.file:
        return certificate

    # 1️⃣ Render HTML
    html_string = render_to_string(
        "certificates/certificate_pdf.html",
        {"certificate": certificate}
    )

    # 2️⃣ Generate PDF bytes
    pdf_bytes = HTML(
        string=html_string,
        base_url=settings.BASE_DIR  # ✅ IMPORTANT FIX
    ).write_pdf()

    # 3️⃣ Create filename
    filename = f"certificate_{certificate.id}.pdf"

    # 4️⃣ Save to FileField
    certificate.file.save(
        filename,
        ContentFile(pdf_bytes),
        save=True
    )

    return certificate
