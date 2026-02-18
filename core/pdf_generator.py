# Create PDF from Resume Markdown file
import os
from markdown import markdown
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

class PDFGenerator:
    def __init__(self):
        self.user_name = os.getenv("USER_FULL_NAME", "Resume")

    def convert_resume(self, md_content, job_title, output_path):
        # Format filename: Name_Job_Title.pdf
        clean_title = job_title.replace(" ", "_").replace("/", "-")
        filename = f"{self.user_name}_{clean_title}.pdf"
        final_pdf_path = os.path.join(output_path, filename)

        # Convert Markdown to HTML
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 40px; color: #333; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; }}
                    h2 {{ color: #34495e; margin-top: 20px; }}
                    li {{ margin-bottom: 5px; }}
                </style>
            </head>
            <body>{markdown(md_content)}</body>
        </html>
        """

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            page.pdf(path=final_pdf_path, format="A4", print_background=True)
            browser.close()
        
        return final_pdf_path