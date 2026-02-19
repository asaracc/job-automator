# Job Automator

Automated application tool.

## Project Map

```text
job-automator/
├── .env                      # Configuration: Stores credentials, API keys, and target URLs
├── .gitignore                # Byte-compiled / optimized / DLL files
├── README.md                 # Job Automator
├── main.py                   # Main Module: Orchestrates the scraping and AI workflow
├── requirements.txt
├── setup.sh                  # Install everything needed in the project
├── core/
│   ├── __init__.py           # Core: Initialization for the core logic package
│   ├── base_board.py         # BaseBoard: Abstract base class for all scraper implementations
│   ├── factory.py            # Factory: Pattern for creating different job board scrapers
│   ├── file_manager.py       # FileManager: Handles directory creation and file saving logic
│   ├── pdf_generator.py      # Create PDF from Resume Markdown file
├── ai/
│   ├── __init__.py           # AI: Initialization for the artificial intelligence package
│   ├── writer.py             # AI Writer: Logic for generating cover letters and parsing JDs
├── scrapers/
│   ├── __init__.py           # Scrapers: Initialization for the scraper package
│   ├── factory.py            # scrapers/factory.py
│   ├── linkedin.py
│   ├── linkedin_manual.py    # LinkedIn: Scraper implementation specific to LinkedIn
```
