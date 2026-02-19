# FileManager: Handles directory creation and file saving logic
# core/file_manager.py
import os
import json
import re # Importado para limpar nomes de pastas
from datetime import datetime
from core.pdf_generator import PDFGenerator

class JobFileManager:
    def __init__(self, base_path="zzz_output"):
        self.base_path = base_path
        self.pdf_gen = PDFGenerator()

    def save_all(self, job_data, ai_res):
        # 1. Nome de pasta robusto (Remove caracteres proibidos em Windows/Linux/Mac)
        date_str = datetime.now().strftime("%Y%m%d")
        raw_name = f"{job_data['company']} - {job_data['title']} - {date_str}"
        # Remove caracteres como / \ : * ? " < > |
        clean_folder_name = re.sub(r'[\\/*?:"<>|]', "", raw_name)
        
        path = os.path.join(self.base_path, clean_folder_name)
        os.makedirs(path, exist_ok=True)

        # 2. Extração segura (Evita KeyError se a IA falhar em algum campo)
        files_data = ai_res.get('files', {})
        resume_md = files_data.get('tailored_resume_md', "Conteúdo não gerado")
        cover_letter_md = files_data.get('cover_letter_md', "Conteúdo não gerado")

        # 3. Escrita dos Markdowns
        self._write(path, "1_job_description.md", job_data.get('description', ""))
        self._write(path, "2_tailored_resume.md", resume_md)
        self._write(path, "3_cover_letter.md", cover_letter_md)
        
        # Relatório de Análise
        scores = ai_res.get('scores', {})
        analysis = ai_res.get('analysis', {})
        
        report = f"# Analysis: {job_data['title']}\n\n"
        report += f"Score: {scores.get('original', 0)} -> {scores.get('tailored', 0)}\n\n"
        report += f"### Fit Analysis\n{analysis.get('fit_report', '')}\n\n"
        report += "### Missing Skills (Gaps)\n- " + "\n- ".join(analysis.get('gaps', []))
        self._write(path, "0_analysis_report.md", report)

        # 4. Geração de PDF (Protegido por Try para não travar o JSON se o PDF falhar)
        try:
            print(f"   📄 Gerando PDF para {job_data['title']}...")
            self.pdf_gen.convert_resume(resume_md, job_data['title'], path)
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar PDF: {e}. (Verifique se o PDFGenerator conflita com loops)")

        # 5. Metadata JSON (Seu código estava ótimo aqui, mantive a estrutura)
        metadata = ai_res.get('metadata', {})
        full_metadata = {
            "job_info": {
                "company": job_data['company'],
                "title": job_data['title'],
                "salary": metadata.get('salary'),
                "country": metadata.get('country'),
                "work_model": metadata.get('work_model'),
                "benefits": metadata.get('benefits'),
                "url": job_data.get('url') # Útil guardar a URL original
            },
            "evaluation": {
                "original_score": scores.get('original'),
                "tailored_score": scores.get('tailored'),
                "gaps": analysis.get('gaps'),
                "fit_analysis": analysis.get('fit_report')
            },
            "generated_content": {
                "resume_markdown": resume_md,
                "cover_letter_markdown": cover_letter_md,
                "job_description_raw": job_data.get('description')
            }
        }

        with open(os.path.join(path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(full_metadata, f, indent=4, ensure_ascii=False)

    def _write(self, path, filename, content):
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)
