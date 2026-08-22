"""
Generator for LEAD documents.
"""
import os, random
from datetime import datetime, timedelta
from PIL import Image
from .entity_pools import get_random_company, get_random_counterparty, get_random_location
from .layout_renderer import render_to_pdf, render_to_docx, render_to_png
from .scan_simulator import apply_scan_effects

def generate_single_lead(doc_id: str, config: dict, output_base_dir: str):
    template_num = random.randint(1, 10)
    template_id = f"lead_template_{template_num:02d}"
    industry = random.choice(config.get("industries", ["ECOMMERCE"]))
    country_info = get_random_location()
    currency = random.choice(config.get("currencies", ["USD"]))
    company = get_random_company()
    counterparty = get_random_counterparty()
    is_scanned = random.random() < config.get("scanned_style_ratio", 0.3)
    degradation = random.choice(config.get("degradation_types", ["blur"])) if is_scanned else "none"

    content = {
        "document_id": doc_id,
        "document_type": "LEAD",
        "template_id": template_id,
        "date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        "company_name": company,
        "counterparty_name": counterparty,
        "currency": currency,
        "body_text": f"LEAD CAPTURE & PROSPECT INFORMATION SHEET.\nProspect Name: {counterparty}\nLead Status: QUALIFIED / NEW\n"
                    f"Lead Source: Inbound Web Form / Trade Show\nEstimated Budget: {currency} {random.randint(5000, 100000)}\n"
                    f"Notes: Expressed strong interest in ERP modules and cloud integration."
    }

    rel_dir = os.path.join("LEAD", f"template_{template_num:03d}")
    out_dir = os.path.join(output_base_dir, rel_dir)
    pdf_path, docx_path, png_path = os.path.join(out_dir, f"{doc_id.lower()}.pdf"), os.path.join(out_dir, f"{doc_id.lower()}.docx"), os.path.join(out_dir, f"{doc_id.lower()}.png")

    render_to_pdf(content, pdf_path)
    render_to_docx(content, docx_path)
    render_to_png(content, png_path)

    if is_scanned:
        img = Image.open(png_path)
        apply_scan_effects(img, degradation).save(png_path)

    record = {
        "document_id": doc_id,
        "file_path_pdf": os.path.join("raw", rel_dir, f"{doc_id.lower()}.pdf"),
        "file_path_docx": os.path.join("raw", rel_dir, f"{doc_id.lower()}.docx"),
        "file_path_png": os.path.join("raw", rel_dir, f"{doc_id.lower()}.png"),
        "document_type": "LEAD",
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
    gt_data = {"document_id": doc_id, "lead_id": doc_id, "company_name": company, "prospect_name": counterparty}
    return record, gt_data
