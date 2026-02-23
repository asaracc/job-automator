# 🚀 Job Automator AI (Beta)

An intelligent automation system for job analysis and application tailoring. This project leverages next-generation AI (Google Gemini) and browser automation (Playwright) to transform LinkedIn links into comprehensive application packages.

# 🛠️ Technologies

Python 3.10+

Playwright: Automation and Scraping from LinkedIn.

Google Gemini API: Artificial Inteligence for written analysis.

xhtml2pdf: Professionals documents creation.

Pandas: Managing Local Data Storage (CSV Master).

# ⚙️ Inicial Configuration

1. Install

Bash

        pip install -r requirements.txt
        playwright install chromium

2. Environment Variables

Create the `.env` file in the root folder.

Code Snippet

        GEMINI_API_KEY=sua_chave_aqui
        GEMINI_MODEL_NAME=gemini-2.0-flash
        USER_FULL_NAME="Seu Nome Completo"

3. Base Resume / CV

Make sure that you Resume/CV text is in 
`assets/resume.txt` (simple text format).

# 🚀 How to Use

## Main usage (Scrapping Jobs)
to process a list of jobs filtered on LinkedIn:

Bash
        
        python main.py

The system will open a new Browser, interate through all left list, extract the information and will create all docs in the `zzz_output` folder.

## Sync after manual edition

If you edit the Markdown files (.md) in one folder and need to update the PDF, the JSON and the CSV.

Bash

        python sync_utils.py zzz_output/"Nome_Da_Pasta_Da_Vaga"

# 📂 Output Structure (zzz_output)

Each Job creates one folder containing the folloing files:

- 0_analysis_report.md: Report with Score, Technical Gaps and Mitigation Strategy.

- 1_job_description.md: Original Job Description for reference.

- 2_tailored_resume.md / .pdf: Resume/CV optimized for this position.

- 3_cover_letter.md / .pdf: Personalized Cover letter.

- metadata.json: All data in a structured file ready to be inserted if needed.

# 📊 Data Repository (Master Log)

The file `applications_master_log.csv` is the local master data. It's storage all history, text backup and columns to control the CRM (Status, Application Date, Notes, etc).

# Get the project Tree

bash

        tree



[!IMPORTANT]

Even if you drop the `zzz_output` all your data still in the CSV file.

# 🏗️ Roadmap PaaS
[ ] Rebuild System: Script para reconstruir pastas e PDFs a partir do CSV.

[ ] Web Dashboard: Interface web para visualizar o CSV Master.

[ ] PostgreSQL Sync: Migração do CSV para banco de dados relacional.

## Project Map

```text
job-automator/
├── .env                           # Configuration: Stores credentials, API keys, and target URLs
├── .gitignore                     # Byte-compiled / optimized / DLL files
├── README.md                      # 🚀 Job Automator AI (Beta)
├── applications_master_log.csv
├── main.py                        # Main Module: Orchestrates the scraping and AI workflow
├── requirements.txt
├── setup.sh                       # Install everything needed in the project
├── sync_utils.py                  # sync_utils.py
├── core/
│   ├── __init__.py                # Core: Initialization for the core logic package
│   ├── base_board.py              # BaseBoard: Abstract base class for all scraper implementations
│   ├── factory.py                 # Factory: Pattern for creating different job board scrapers
│   ├── file_manager.py            # core/file_manager.py
│   ├── pdf_generator.py           # Create PDF from Resume Markdown file
├── ai/
│   ├── __init__.py                # AI: Initialization for the artificial intelligence package
│   ├── writer.py                  # AI Writer: Logic for generating cover letters and parsing JDs
├── scrapers/
│   ├── __init__.py                # Scrapers: Initialization for the scraper package
│   ├── factory.py                 # scrapers/factory.py
│   ├── linkedin.py
│   ├── linkedin_manual.py         # LinkedIn: Scraper implementation specific to LinkedIn
```
