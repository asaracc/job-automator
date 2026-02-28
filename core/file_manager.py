"""
core/file_manager.py
Handles the creation of directories and persistence of job application data.
Integrates job_hash for deterministic tracking and prevents duplicate processing.
"""

import os
import json
import re
import csv
from datetime import datetime
from core.pdf_generator import PDFGenerator


class JobFileManager:
    def __init__(self, base_path="zzz_output"):
        self.base_path = base_path
        self.pdf_gen = PDFGenerator()
        # The CSV remains in the project root for safety and easy access
        self.master_csv_path = "applications_master_log.csv"

    def save_all(self, job_data, ai_res, job_hash):
        """
        Saves all job-related files, generates PDFs, and updates the Master CSV.
        Now requires job_hash to ensure unique identification.
        """
        # 1. Folder Setup (YYYYMMDD-Company-Title-HashShort)
        date_str = datetime.now().strftime("%Y%m%d")
        clean_company = re.sub(r'[\\/*?:"<>|]', "", job_data['company']).replace(' ', '_')
        clean_job_title = re.sub(r'[\\/*?:"<>|]', "", job_data['title']).replace(' ', '_')

        folder_name = f"{date_str}-{clean_company}-{clean_job_title}-{job_hash[:8]}"
        path = os.path.join(self.base_path, folder_name)
        os.makedirs(path, exist_ok=True)

        # 2. Data Extraction
        files_data = ai_res.get('files', {})
        resume_md = files_data.get('tailored_resume_md', "")
        cover_letter_md = files_data.get('cover_letter_md', "")

        # 3. Save Physical Markdown Files
        self._write(path, "1_job_description.md", job_data.get('description', ""))
        self._write(path, "2_tailored_resume.md", resume_md)
        self._write(path, "3_cover_letter.md", cover_letter_md)
        
        report = self._build_human_report(job_data, ai_res)
        self._write(path, "0_analysis_report.md", report)

        # 4. PDF Generation
        try:
            print(f"   📄 Generating PDFs for {job_data['title']}...")
            self.pdf_gen.convert_resume(resume_md, f"Resume_{job_data['title']}", path)
            self.pdf_gen.convert_resume(cover_letter_md, f"CoverLetter_{job_data['title']}", path)
        except Exception as e:
            print(f"   ⚠️ PDF Error: {e}")

        # 5. Build and Save Metadata JSON (FIXED: Now passes and uses job_hash)
        full_metadata = self._build_metadata_dict(job_data, ai_res, job_hash)
        with open(os.path.join(path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(full_metadata, f, indent=4, ensure_ascii=False)

        # 6. Update Master CSV
        self._update_master_csv(full_metadata)

    def _update_master_csv(self, data):
        """Flattens metadata dictionary for CSV row appending."""
        row = {
            "job_hash": data["application_meta"]["job_hash"],
            "date_generated": data["application_meta"]["timestamp"],
            "company": data["job_info"]["company"],
            "title": data["job_info"]["title"],
            "salary": data["job_info"]["salary"],
            "country": data["job_info"]["country"],
            "work_model": data["job_info"]["work_model"],
            "apply_method": data["job_info"]["apply_method"],
            "url": data["job_info"]["url"],
            "original_score": data["evaluation"]["original_score"],
            "tailored_score": data["evaluation"]["tailored_score"],
            "gaps": "|".join(data["evaluation"]["gaps"]),
            "mitigation_strategy": data["evaluation"]["mitigation_strategy"],
            "resume_content_md": data["generated_content"]["resume_markdown"],
            "cover_letter_md": data["generated_content"]["cover_letter_markdown"],
            "job_description_raw": data["generated_content"]["job_description_raw"],
            "status": "Generated",
            "applied_date": "", 
            "contact_person": "",
            "interview_date": "",
            "next_steps": "",
            "notes": ""
        }

        file_exists = os.path.isfile(self.master_csv_path)
        with open(self.master_csv_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        print(f"   📊 Job registered in Master CSV with Hash: {row['job_hash'][:8]}")

    def _build_metadata_dict(self, job_data, ai_res, job_hash):
        """
        FIXED: Added job_hash parameter and replaced legacy 'id'.
        This matches the structure expected by sync_utils.py.
        """
        metadata_ai = ai_res.get('metadata', {})
        return {
            "application_meta": {
                "job_hash": job_hash,
                "timestamp": datetime.now().isoformat()
            },
            "job_info": {
                "company": job_data['company'],
                "title": job_data['title'],
                "salary": metadata_ai.get('salary'),
                "country": metadata_ai.get('country'),
                "work_model": metadata_ai.get('work_model'),
                "benefits": metadata_ai.get('benefits'),
                "url": job_data.get('url'),
                "apply_method": metadata_ai.get('apply_instructions')
            },
            "evaluation": {
                "original_score": ai_res.get('scores', {}).get('original'),
                "tailored_score": ai_res.get('scores', {}).get('tailored'),
                "gaps": ai_res.get('analysis', {}).get('gaps', []),
                "fit_analysis": ai_res.get('analysis', {}).get('fit_report'),
                "mitigation_strategy": ai_res.get('analysis', {}).get('mitigation_strategy')
            },
            "generated_content": {
                "resume_markdown": ai_res.get('files', {}).get('tailored_resume_md'),
                "cover_letter_markdown": ai_res.get('files', {}).get('cover_letter_md'),
                "job_description_raw": job_data.get('description')
            }
        }

    def _build_human_report(self, job_data, ai_res):
        """
        Generates a readable Markdown report summarizing the AI analysis 
        of the job application and the candidate's fit.
        """
        scores = ai_res.get('scores', {})
        analysis = ai_res.get('analysis', {})
        metadata_ai = ai_res.get('metadata', {})
        report = f"# 📊 Application Analysis: {job_data['title']}\n\n"
        # Match Score comparison
        report += f"**Match Score:** {scores.get('original', 0)} → **Optimized:** {scores.get('tailored', 0)}\n\n"
        # Application Instructions
        report += f"## 🛠️ How to Apply\n{metadata_ai.get('apply_instructions', 'Verify application link.')}\n\n"
        # Fit Analysis section
        report += f"### 🧐 Fit Analysis\n{analysis.get('fit_report', '')}\n\n"
        # Gaps / Missing Requirements
        report += "### ⚠️ Gaps & Missing Skills\n- " + "\n- ".join(analysis.get('gaps', [])) + "\n\n"
        # Strategy for overcoming gaps
        report += f"### 💡 Mitigation Strategy\n{analysis.get('mitigation_strategy', '')}\n"

        return report

    def _write(self, path, filename, content):
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)
