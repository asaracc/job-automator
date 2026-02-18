# FileManager: Handles directory creation and file saving logic
import os
import json
from datetime import datetime
from core.pdf_generator import PDFGenerator


class JobFileManager:
    def __init__(self, base_path="zzz_output"):
        self.base_path = base_path
        self.pdf_gen = PDFGenerator()

    def save_all(self, job_data, ai_res):
        # 1. Create folder
        date_str = datetime.now().strftime("%Y%m%d")
        folder_name = f"{job_data['company']} - {job_data['title']} - {date_str}".replace("/", "-")
        path = os.path.join(self.base_path, folder_name)
        os.makedirs(path, exist_ok=True)

        # 2. Check content
        resume_md = ai_res['files']['tailored_resume_md']
        cover_letter_md = ai_res['files']['cover_letter_md']

        # 3. Create files (Markdown and PDF)
        self._write(path, "1_job_description.md", job_data['description'])
        self._write(path, "2_tailored_resume.md", resume_md)
        self._write(path, "3_cover_letter.md", cover_letter_md)
        
        report = f"# Analysis: {job_data['title']}\n\n"
        report += f"Score: {ai_res['scores']['original']} -> {ai_res['scores']['tailored']}\n\n"
        report += f"### Fit Analysis\n{ai_res['analysis']['fit_report']}\n\n"
        report += "### Missing Skills (Gaps)\n- " + "\n- ".join(ai_res['analysis']['gaps'])
        self._write(path, "0_analysis_report.md", report)

        # Create PDF
        self.pdf_gen.convert_resume(resume_md, job_data['title'], path)

        # 4. Load all into Json (Including MDs)
        full_metadata = {
            "job_info": {
                "company": job_data['company'],
                "title": job_data['title'],
                "salary": ai_res['metadata'].get('salary'),
                "country": ai_res['metadata'].get('country'),
                "work_model": ai_res['metadata'].get('work_model'),
                "benefits": ai_res['metadata'].get('benefits'),
            },
            "evaluation": {
                "original_score": ai_res['scores']['original'],
                "tailored_score": ai_res['scores']['tailored'],
                "gaps": ai_res['analysis']['gaps'],
                "fit_analysis": ai_res['analysis']['fit_report']
            },
            "generated_content": {
                "resume_markdown": resume_md,
                "cover_letter_markdown": cover_letter_md,
                "job_description_raw": job_data['description']
            }
        }

        with open(os.path.join(path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(full_metadata, f, indent=4, ensure_ascii=False)

    def _write(self, path, filename, content):
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)