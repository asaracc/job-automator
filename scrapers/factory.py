# scrapers/factory.py
from scrapers.linkedin import LinkedInScraper


class ScraperFactory:  # <-- O nome tem que ser idêntico ao do import
    @staticmethod
    def get_scraper(url: str):
        if "linkedin.com" in url:
            return LinkedInScraper()
        else:
            raise ValueError(f"❌ Site não suportado: {url}")