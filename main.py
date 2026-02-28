"""
main.py
Main Module: Orchestrates the scraping and AI workflow.
Integrates SHA-256 hashing to prevent duplicate job processing.
Now automated with Search Matrix from config.py.
"""

from concurrent.futures import ThreadPoolExecutor
from ai.writer import AIWriter
from core.file_manager import JobFileManager
from scrapers.linkedin import LinkedInScraper
from core.utils import generate_job_hash
# Added COOLDOWN import to manage search frequency safely
from config import SEARCH_MATRIX, MAX_PAGES_PER_SEARCH
import pandas as pd
import os
import urllib.parse
import time

MASTER_CSV = "applications_master_log.csv"


def build_url(config):
    """
    Encodes config dict into a valid LinkedIn search URL.
    """
    base = "https://www.linkedin.com/jobs/search/?"
    params = {
        "keywords": config["keywords"],
        "geoid": config["geoId"],
        "f_WT": config.get("f_WT", "2"),  # Default Remote
        "f_TPR": config.get("f_TPR", "r604800") # Default Last 7 Days
    }
    # Add optional experience level if it exists in config
    if "f_E" in config:
        params["f_E"] = config["f_E"]
        
    return base + urllib.parse.urlencode(params)


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

    print("\n" + "="*60)
    print("🚀 BATTLE PLAN: PRE-FLIGHT CHECK")
    print("="*60)
    
    # Pre-generate and print all URLs for verification
    active_urls = []
    for i, config in enumerate(SEARCH_MATRIX, 1):
        url = build_url(config)
        active_urls.append((config, url))
        print(f"{i}. 🔍 {config['keywords']} in geoId {config['geoId']}")
        print(f"   🔗 {url}\n")
    
    print(f"📊 Total combinations to process: {len(SEARCH_MATRIX)}")
    print("="*60)
    
    # Small pause so you can actually read the URLs before it starts
    time.sleep(3)

    print("\n" + "="*50)
    print("🚀 Automatic Application Generator started.")
    print(f"📊 Loaded {len(SEARCH_MATRIX)} search combinations from config.")
    print("="*50 + "\n")

    try:
        # --- NEW AUTOMATED LOOP START ---
        for search_item in SEARCH_MATRIX:
            search_url = build_url(search_item)
            
            print(f"\n🔍 STARTING SEARCH: {search_item['keywords']} in {search_item['geoId']}")
            print(f"🔗 URL: {search_url}")

            # 3. Scraping Loop Start
            # Using the automated URL and the MAX_PAGES_PER_SEARCH from config
            for i, job_data in enumerate(scraper.scrape_search_results(search_url, max_pages=MAX_PAGES_PER_SEARCH), 1):
                # 1. Capture basic info
                title = job_data.get('title', 'unknown')
                company = job_data.get('company', 'unknown')
                description = job_data.get('description', '')

                # 2. Skip if description is empty or failed (English match)
                if not description or description == "unknown" or description == "Not found":
                    print(f"  ⏭️  [SKIP] '{title}': Description not found.")
                    continue

                # 3. Generate unique hash
                job_hash = generate_job_hash(company, title, description)

                # 4. Check if already handled
                if is_already_processed(job_hash):
                    print(f"  ✅ [ALREADY PROCESSED] {title} @ {company} ({job_hash[:8]})")
                    continue

                # 5. Process new job with visual separation
                print("\n" + "─"*50)
                print(f"🚀 [PROCESSING NEW JOB] {title.upper()}")
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
            
            # Optional: Short cooldown between different keyword searches
            print(f"\n✅ Finished search for '{search_item['keywords']}'. Moving to next...")
            time.sleep(5) 
            
        # --- AUTOMATED LOOP END ---

        print("\n" + "="*50)
        print("🏁 All search combinations completed successfully!")
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
