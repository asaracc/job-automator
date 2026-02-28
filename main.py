"""
main.py
Main Module: Orchestrates the scraping and AI workflow.
Integrates SHA-256 hashing to prevent duplicate job processing.
"""

from concurrent.futures import ThreadPoolExecutor
from ai.writer import AIWriter
from core.file_manager import JobFileManager
from scrapers.linkedin import LinkedInScraper
from core.utils import generate_job_hash
import pandas as pd
import os

MASTER_CSV = "applications_master_log.csv"


def is_already_processed(job_hash):
    """
    Checks the Master CSV to prevent redundant AI processing.
    Cleans column names to ensure 'job_hash' is found correctly.
    """
    if not os.path.exists(MASTER_CSV):
        return False
    try:
        # Read only the 'job_hash' column to save memory
        df = pd.read_csv(MASTER_CSV, usecols=['job_hash'])
        # Clean potential whitespace from the data and check existence
        return job_hash in df['job_hash'].values
    except ValueError:
        # This happens if 'job_hash' column doesn't exist yet
        print(f"⚠️  Warning: 'job_hash' column not found in {MASTER_CSV}.")
        return False
    except Exception as e:
        print(f"⚠️  Error reading Master Log: {e}")
        return False


def main():
    # 1. Component Initialization
    writer = AIWriter()
    manager = JobFileManager()
    scraper = LinkedInScraper()

    # The executor isolates AI tasks in a separate thread to solve asyncio loop conflicts
    executor = ThreadPoolExecutor(max_workers=1)

    print("🚀 Automatic Application Generator started.")

    # 2. LinkedIn Search URL Input
    search_url = input("Paste your LinkedIn filtered search URL: ").strip()

    if not search_url:
        print("❌ Invalid URL.")
        return

    try:
        # 3. Scraping Loop Start
        # The scraper yields job_data dynamically
        for i, job_data in enumerate(scraper.scrape_search_results(search_url), 1):
            # 1. Capture basic info
            title = job_data.get('title', 'unknown')
            company = job_data.get('company', 'unknown')
            description = job_data.get('description', '')

            # 2. Skip if description is empty or failed (English match)
            if not description or description == "unknown":
                print(f"  ⏭️  [SKIP] '{title}': Description not found.")
                continue

            # 3. Generate unique hash
            job_hash = generate_job_hash(company, title, description)

            # 2. Check if already handled
            if is_already_processed(job_hash):
                print(f". ✅ [ALREADY PROCESSED] {title} @ {company} ({job_hash[:8]})")
                continue

            # 3. Process new job with visual separation
            print("\n" + "─"*50)
            print(f"🚀 [JOB {i}] {title.upper()}")
            print(f"🏢 COMPANY: {company}")
            print(f"🆔 HASH:    {job_hash[:8]}")
            print("─"*50)

            try:
                print("   🤖 AI Analysis in progress...")
                future = executor.submit(writer.process_application, description, title, company)
                results = future.result()

                print("   📄 Exporting Files & PDFs...")
                manager.save_all(job_data, results, job_hash)

                print(f"   ✨ SUCCESS: Application generated for {company}")

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                continue

        print("\n" + "="*50)
        print("🏁 Operation completed successfully!")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Critical system failure: {e}")
    finally:
        # Cleanly shutdown the thread executor
        executor.shutdown(wait=True)


if __name__ == "__main__":
    main()
