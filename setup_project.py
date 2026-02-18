import os


def create_setup():
    # Folder structure (including assets and zzz_output)
    folders = ["core", "scrapers", "ai", "zzz_output", "assets"]

    # Dictionary: Path -> Header Comment in English
    files_to_create = {
        "main.py": "# Main Module: Orchestrates the scraping and AI workflow",
        ".env": "# Configuration: Stores credentials, API keys, and target URLs",
        "requirements.txt": "# Dependencies: Project library requirements",
        "core/__init__.py": "# Core: Initialization for the core logic package",
        "core/factory.py": "# Factory: Pattern for creating different job board scrapers",
        "core/base_board.py": "# BaseBoard: Abstract base class for all scraper implementations",
        "core/file_manager.py": "# FileManager: Handles directory creation and file saving logic",
        "scrapers/__init__.py": "# Scrapers: Initialization for the scraper package",
        "scrapers/linkedin.py": "# LinkedIn: Scraper implementation specific to LinkedIn",
        "ai/__init__.py": "# AI: Initialization for the artificial intelligence package",
        "ai/writer.py": "# AI Writer: Logic for generating cover letters and parsing JDs",
        "assets/resume.txt": "# Assets: Your base resume text for AI context"
    }

    # Create directories
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create files only if they do not exist
    for path, comment in files_to_create.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"{comment}\n")
            print(f"✅ Created: {path}")
        else:
            print(f"⚠️ Skipping (already exists): {path}")


if __name__ == "__main__":
    create_setup()
