"""
scripts/sync_utils.py
Utility to sync Markdown edits back to JSON/CSV and regenerate PDFs.
"""

import os
import sys
import json
import re
import pandas as pd
from dotenv import load_dotenv
from core.pdf_generator import PDFGenerator

load_dotenv()


def clean_name(text):
    """Normalizes names for filesystem and PDF naming consistency."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = text.replace(" - ", "_").replace(" ", "_").replace("-", "_")
    return re.sub(r'_+', '_', text).strip('_')


def sync_all_from_folder(folder_path):
    """
    Synchronizes manual .md edits back to the Master CSV and JSON metadata.
    Uses 'job_hash' to ensure we update the correct record.
    """
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist.")
        return

    # 1. Load metadata
    metadata_path = os.path.join(folder_path, "metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ Error: metadata.json not found.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        local_metadata = json.load(f)

    # Identifier check
    job_hash = local_metadata["application_meta"].get("job_hash")
    job_title = local_metadata["job_info"]["title"]
    company = local_metadata["job_info"]["company"]
    master_csv = "applications_master_log.csv"

    # 2. Map MD files to JSON keys (match generated_content structure)
    sync_map = {
        "2_tailored_resume.md": ("resume_markdown", "Resume"),
        "3_cover_letter.md": ("cover_letter_markdown", "Cover_Letter")
    }

    updated_contents = {}
    any_changes = False

    for filename, (json_key, doc_type) in sync_map.items():
        md_path = os.path.join(folder_path, filename)
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Update updated_contents for PDF generation later
            updated_contents[doc_type] = content

            # Check if the text was changed compared to the JSON record
            if local_metadata["generated_content"].get(json_key) != content:
                local_metadata["generated_content"][json_key] = content
                any_changes = True

    # 3. Persistence: Save to JSON and CSV
    if any_changes:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(local_metadata, f, indent=4, ensure_ascii=False)

        if os.path.exists(master_csv):
            df = pd.read_csv(master_csv)
            if "job_hash" in df.columns and job_hash in df["job_hash"].values:
                mask = df["job_hash"] == job_hash
                # Update CSV columns (ensuring column names match JobFileManager)
                df.loc[mask, "resume_content_md"] = local_metadata["generated_content"]["resume_markdown"]
                df.loc[mask, "cover_letter_md"] = local_metadata["generated_content"]["cover_letter_markdown"]
                df.to_csv(master_csv, index=False, encoding="utf-8")
                print(f"   📊 Master Log synced for hash: {job_hash[:8]}")

    # 4. Regenerate PDFs
    pdf_gen = PDFGenerator()
    f_company = clean_name(company)
    f_job = clean_name(job_title)

    # Clean up naming redundancy (e.g., Apple_Apple_Engineer -> Apple_Engineer)
    if f_job.lower().startswith(f_company.lower()):
        f_job = f_job[len(f_company):].strip("_")

    print(f"📄 Regenerating PDFs in: {folder_path}...")
    for doc_type, content in updated_contents.items():
        # Final filename structure: Resume_Company_JobTitle
        final_filename = f"{doc_type}_{f_company}_{f_job}"
        try:
            pdf_gen.convert_resume(content, final_filename, folder_path)
            print(f"   ✅ Created: {final_filename}.pdf")
        except Exception as e:
            print(f"   ⚠️ PDF Gen Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sync_utils.py <folder_path>")
    else:
        sync_all_from_folder(sys.argv[1])
