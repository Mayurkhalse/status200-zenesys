"""
Orchestrator for Synthetic Document Generation.
Reads generation_config.yaml and paths_config.yaml, invokes generator for each class,
and outputs dataset/synthetic_data.csv, metadata.jsonl, and extraction ground truths.
"""
import os
import argparse
import yaml
from ml.dataset_generation.csv_writer import append_document_record, append_ground_truth
from ml.dataset_generation.generate_invoice import generate_single_invoice
from ml.dataset_generation.generate_purchase_order import generate_single_purchase_order
from ml.dataset_generation.generate_sales_order import generate_single_sales_order
from ml.dataset_generation.generate_quotation import generate_single_quotation
from ml.dataset_generation.generate_proposal import generate_single_proposal
from ml.dataset_generation.generate_contract import generate_single_contract
from ml.dataset_generation.generate_lead import generate_single_lead
from ml.dataset_generation.generate_receipt import generate_single_receipt
from ml.dataset_generation.generate_delivery_note import generate_single_delivery_note
from ml.dataset_generation.generate_credit_note import generate_single_credit_note
from ml.dataset_generation.generate_debit_note import generate_single_debit_note
from ml.dataset_generation.generate_payment_receipt import generate_single_payment_receipt
from ml.dataset_generation.generate_rfq import generate_single_rfq
from ml.dataset_generation.generate_other import generate_single_other

GENERATORS = {
    "BUSINESS_INVOICE": generate_single_invoice,
    "PURCHASE_ORDER": generate_single_purchase_order,
    "SALES_ORDER": generate_single_sales_order,
    "QUOTATION": generate_single_quotation,
    "PROPOSAL": generate_single_proposal,
    "CONTRACT": generate_single_contract,
    "LEAD": generate_single_lead,
    "RECEIPT": generate_single_receipt,
    "DELIVERY_NOTE": generate_single_delivery_note,
    "CREDIT_NOTE": generate_single_credit_note,
    "DEBIT_NOTE": generate_single_debit_note,
    "PAYMENT_RECEIPT": generate_single_payment_receipt,
    "RFQ": generate_single_rfq,
    "OTHER": generate_single_other
}

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ERP business documents.")
    parser.add_argument("--config", default="config/generation_config.yaml", help="Path to generation config")
    parser.add_argument("--paths", default="config/paths_config.yaml", help="Path to canonical paths config")
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        gen_config = yaml.safe_load(f)
    with open(args.paths, 'r', encoding='utf-8') as f:
        paths_config = yaml.safe_load(f)

    docs_per_class = gen_config.get("documents_per_class", 10)
    raw_dir = paths_config["dataset"]["raw_dir"]
    csv_path = paths_config["dataset"]["synthetic_csv"]
    jsonl_path = paths_config["dataset"]["metadata_jsonl"]
    gt_dir = paths_config["dataset"]["ground_truth_dir"]

    # Clear existing synthetic metadata if fresh run
    if os.path.exists(csv_path):
        os.remove(csv_path)
    if os.path.exists(jsonl_path):
        os.remove(jsonl_path)

    doc_counter = 1
    classes = gen_config.get("document_classes", list(GENERATORS.keys()))

    print(f"Starting document generation: {docs_per_class} docs per class across {len(classes)} classes...")
    for doc_class in classes:
        generator_fn = GENERATORS.get(doc_class, generate_single_other)
        for i in range(docs_per_class):
            doc_id = f"DOC_{doc_counter:06d}"
            record, gt_data = generator_fn(doc_id, gen_config, raw_dir)
            append_document_record(record, csv_path, jsonl_path)
            append_ground_truth(doc_class, gt_data, gt_dir)
            doc_counter += 1

    print(f"Successfully generated {doc_counter - 1} documents.")
    print(f"CSV saved to: {csv_path}")
    print(f"JSONL saved to: {jsonl_path}")

if __name__ == "__main__":
    main()
