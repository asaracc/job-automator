# Create PDF from Resume Markdown file
# core/pdf_generator.py
# core/pdf_generator.py
import os
import re
from markdown import markdown
from xhtml2pdf import pisa


class PDFGenerator:
    def __init__(self):
        self.user_name = os.getenv("USER_FULL_NAME", "Candidato")

    def convert_resume(self, md_content, job_title, output_path):
        # 1. Preparar nome do arquivo
        clean_title = re.sub(r'[\\/*?:"<>|]', "", job_title).replace(" ", "_")
        filename = f"{self.user_name}_{clean_title}.pdf"
        final_pdf_path = os.path.join(output_path, filename)

        # 2. Converter Markdown para HTML
        html_body = markdown(md_content, extensions=['extra', 'smarty'])

        # 3. HTML completo (SEM o bloco centralizado duplicado)
        full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: a4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 10pt;
                    line-height: 1.4;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 18pt;
                    margin-bottom: 5pt;
                    text-align: left; /* Alinha com o padrão do MD */
                }}
                h3 {{
                    color: #2c3e50;
                    margin-top: 15pt;
                    border-bottom: 1px solid #eee;
                    font-size: 12pt;
                }}
                b, strong {{
                    color: #000;
                }}
                ul {{
                    padding-left: 15pt;
                }}
                li {{
                    margin-bottom: 4pt;
                }}
                p {{
                    margin-bottom: 8pt;
                }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # 4. Gerar o PDF
        with open(final_pdf_path, "wb") as result_file:
            pisa_status = pisa.CreatePDF(full_html, dest=result_file)

        if pisa_status.err:
            raise Exception(f"Erro ao gerar PDF: {pisa_status.err}")

        return final_pdf_path
