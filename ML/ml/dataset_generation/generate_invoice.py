"""
Generator for BUSINESS_INVOICE documents.
"""
import os
import random
from datetime import datetime, timedelta
from PIL import Image
from .entity_pools import get_random_company, get_random_counterparty, get_random_location, get_random_items, PAYMENT_TERMS_LIST
from .layout_renderer import render_to_pdf, render_to_docx, render_to_png
from .scan_simulator import apply_scan_effects

def generate_single_invoice(doc_id: str, config: dict, output_base_dir: str):
    template_num = random.randint(1, 10)
    template_id = f"invoice_template_{template_num:02d}"
    industry = random.choice(config.get("industries", ["IT_SERVICES"]))
    country_info = get_random_location()
    currency = random.choice(config.get("currencies", ["USD"]))
    company = get_random_company()
    counterparty = get_random_counterparty()
    items = get_random_items(industry=industry, count=random.randint(2, 5))
    total_amount = sum(item["total_price"] for item in items)
    
    is_scanned = random.random() < config.get("scanned_style_ratio", 0.3)
    degradation = random.choice(config.get("degradation_types", ["blur"])) if is_scanned else "none"

    content = {
        "document_id": doc_id,
        "document_type": "BUSINESS_INVOICE",
        "template_id": template_id,
        "date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        "company_name": company,
        "counterparty_name": counterparty,
        "currency": currency,
        "payment_terms": random.choice(PAYMENT_TERMS_LIST),
        "items": items,
        "total_amount": total_amount,
        "body_text": f"TAX INVOICE / BILL OF SUPPLY.\nPlease remit payment within the agreed terms. Invoice Ref: {doc_id}."
    }

    rel_dir = os.path.join("BUSINESS_INVOICE", f"template_{template_num:03d}")
    out_dir = os.path.join(output_base_dir, rel_dir)
    
    pdf_path = os.path.join(out_dir, f"{doc_id.lower()}.pdf")
    docx_path = os.path.join(out_dir, f"{doc_id.lower()}.docx")
    png_path = os.path.join(out_dir, f"{doc_id.lower()}.png")

    render_to_pdf(content, pdf_path)
    render_to_docx(content, docx_path)
    render_to_png(content, png_path)

    if is_scanned:
        img = Image.open(png_path)
        degraded_img = apply_scan_effects(img, degradation)
        degraded_img.save(png_path)

    record = {
        "document_id": doc_id,
        "file_path_pdf": os.path.join("raw", rel_dir, f"{doc_id.lower()}.pdf"),
        "file_path_docx": os.path.join("raw", rel_dir, f"{doc_id.lower()}.docx"),
        "file_path_png": os.path.join("raw", rel_dir, f"{doc_id.lower()}.png"),
        "document_type": "BUSINESS_INVOICE",
        "template_id": template_id,
        "industry": industry,
        "country": country_info["country"],
        "currency": currency,
        "company_name": company,
        "counterparty_name": counterparty,
        "is_scanned_style": is_scanned,
        "degradation_type": degradation,
        "generated_at": datetime.now().isoformat(),
        "generator_version": config.get("generator_version", "1.0.0")
    }

    gt_data = {
        "document_id": doc_id,
        "invoice_number": doc_id,
        "invoice_date": content["date"],
        "company_name": company,
        "counterparty_name": counterparty,
        "total_amount": total_amount,
        "currency": currency
    }

    return record, gt_data
