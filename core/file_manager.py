# core/file_manager.py
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
        # O CSV fica na raiz do projeto, fora da pasta de output para segurança
        self.master_csv_path = "applications_master_log.csv"

    def save_all(self, job_data, ai_res):
        # 1. Setup de Pastas
        date_str = datetime.now().strftime("%Y%m%d")
        raw_name = f"{job_data['company']} - {job_data['title']} - {date_str}"
        clean_folder_name = re.sub(r'[\\/*?:"<>|]', "", raw_name)
        path = os.path.join(self.base_path, clean_folder_name)
        os.makedirs(path, exist_ok=True)

        # 2. Extração de Dados
        files_data = ai_res.get('files', {})
        resume_md = files_data.get('tailored_resume_md', "")
        cover_letter_md = files_data.get('cover_letter_md', "")

        # 3. Salvar Arquivos Físicos (Markdown)
        self._write(path, "1_job_description.md", job_data.get('description', ""))
        self._write(path, "2_tailored_resume.md", resume_md)
        self._write(path, "3_cover_letter.md", cover_letter_md)
        
        report = self._build_human_report(job_data, ai_res)
        self._write(path, "0_analysis_report.md", report)

        # 4. Geração de PDFs (NOVO: Resume e Cover Letter)
        try:
            print(f"   📄 Gerando PDFs para {job_data['title']}...")
            # Gera o PDF do Currículo
            self.pdf_gen.convert_resume(resume_md, f"Resume_{job_data['title']}", path)
            # Gera o PDF da Carta de Apresentação
            self.pdf_gen.convert_resume(cover_letter_md, f"CoverLetter_{job_data['title']}", path)
        except Exception as e:
            print(f"   ⚠️ Erro PDF: {e}")

        # 5. Gerar o JSON
        full_metadata = self._build_metadata_dict(job_data, ai_res)
        with open(os.path.join(path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(full_metadata, f, indent=4, ensure_ascii=False)

        # 6. Atualizar CSV Master
        self._update_master_csv(full_metadata)

    def _update_master_csv(self, data):
        # Flattening do dicionário para colunas de CSV
        # Incluímos colunas de controle de status que você pediu
        row = {
            "app_id": data["application_meta"]["id"],
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
            "gaps": "|".join(data["evaluation"]["gaps"]), # Pipe separator para lista
            "mitigation_strategy": data["evaluation"]["mitigation_strategy"],
            "resume_content_md": data["generated_content"]["resume_markdown"], # Backup do currículo
            "cover_letter_md": data["generated_content"]["cover_letter_markdown"],
            "job_description_raw": data["generated_content"]["job_description_raw"],
            # COLUNAS DE CONTROLE (Status da Aplicação)
            "status": "Generated", # default
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
        print(f"   📊 Vaga registrada no Master CSV: {self.master_csv_path}")

    def _build_metadata_dict(self, job_data, ai_res):
        # Reaproveitando a estrutura JSON que já tínhamos
        metadata_ai = ai_res.get('metadata', {})
        return {
            "application_meta": {
                "id": f"app_{int(datetime.now().timestamp())}",
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
        scores = ai_res.get('scores', {})
        analysis = ai_res.get('analysis', {})
        metadata_ai = ai_res.get('metadata', {})
        report = f"# 📊 Análise de Candidatura: {job_data['title']}\n\n"
        report += f"**Match Score:** {scores.get('original', 0)} → **Otimizado:** {scores.get('tailored', 0)}\n\n"
        report += f"## 🛠️ Como Aplicar\n{metadata_ai.get('apply_instructions', 'Verificar link.')}\n\n"
        report += f"### 🧐 Análise de Fit\n{analysis.get('fit_report', '')}\n\n"
        report += "### ⚠️ Gaps\n- " + "\n- ".join(analysis.get('gaps', [])) + "\n\n"
        report += f"### 💡 Mitigação\n{analysis.get('mitigation_strategy', '')}\n"
        return report

    def _write(self, path, filename, content):
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)