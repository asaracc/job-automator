# Main Module: Orchestrates the scraping and AI workflow
from ai.writer import AIWriter
from core.file_manager import JobFileManager
from scrapers.linkedin import LinkedInScraper # Import the fake scraper


def main():
    writer = AIWriter()
    manager = JobFileManager()
    scraper = LinkedInScraper() # Initialize scraper

    # Now you just provide a fake URL
    job_url = "https://www.linkedin.com/jobs/fake-test"

    try:
        print("🔍 Fetching job details...")
        job_data = scraper.get_job_data(job_url)

        print(f"🚀 Processing application for {job_data['title']} at {job_data['company']}...")
        results = writer.process_application(job_data['description'], job_data['title'], job_data['company'])
        
        manager.save_all(job_data, results)
        print("✅ Everything saved: Markdown, JSON, and PDF!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()