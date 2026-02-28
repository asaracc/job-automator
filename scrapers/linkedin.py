"""
scrapers/linkedin.py
Module for automated LinkedIn job data extraction using Playwright.
Handles session persistence, lazy loading, and data mapping.
"""

import time
import random
from playwright.sync_api import sync_playwright


class LinkedInScraper:
    """
    A scraper class to navigate LinkedIn search results and extract job details.

    Attributes:
        selectors (dict): CSS selectors for various job page elements.
    """

    def __init__(self):
        self.selectors = {
            "job_card": ".scaffold-layout__list-item",
            "title": ".job-details-jobs-unified-top-card__job-title",
            "company": ".job-details-jobs-unified-top-card__company-name",
            "description": ".jobs-description__content",
            "left_container": ".jobs-search-results-list",
            "no_results": ".jobs-search-two-pane__no-results-banner"
        }

    def scrape_search_results(self, base_url, max_pages=3):
        """
        Automated multi-page scraper. 
        No manual input required—uses the URL provided by the Search Matrix.
        """
        with sync_playwright() as p:
            user_data_dir = "./playwright_data"
            browser = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,  # Set to True once you know it's working
                slow_mo=500,
                args=["--start-maximized"]
            )

            page = browser.pages[0]

            for current_page in range(max_pages):
                offset = current_page * 25
                # Ensures the URL has the correct starting point for pagination
                paginated_url = f"{base_url}&start={offset}"
                
                print(f"      📂 [PAGE {current_page + 1}] Accessing: {paginated_url}")
                page.goto(paginated_url, wait_until="domcontentloaded")
                
                # Check if LinkedIn shows 'No results'
                if page.locator(self.selectors["no_results"]).is_visible():
                    print("      🏁 End of results reached.")
                    break

                # Wait for the first job card to appear
                try:
                    page.wait_for_selector(self.selectors["job_card"], timeout=10000)
                except Exception as e:
                    print(f"⚠️  Scroll Warning: {e}")
                    break

                # Human-like scrolling to load the sidebar
                self._scroll_sidebar(page)
                
                cards = page.locator(self.selectors["job_card"]).all()
                for i, card in enumerate(cards):
                    try:
                        card.scroll_into_view_if_needed()
                        card.click()
                        time.sleep(random.uniform(2, 4)) # Mimic reading time

                        yield {
                            "title": self._get_text(page, self.selectors["title"]),
                            "company": self._get_text(page, self.selectors["company"]),
                            "description": self._get_text(page, self.selectors["description"]),
                            "url": page.url
                        }
                    except Exception as e:
                        print(f"      ⚠️  Skip card {i+1}: {e}")
                        continue

            browser.close()

    def _scroll_sidebar(self, page):
        try:
            container = page.locator(self.selectors["left_container"])
            for _ in range(3):
                container.evaluate("node => node.scrollTop += 800")
                time.sleep(0.5)
        except: pass

    def _get_text(self, page, selector):
        """
        Safely extracts inner text from a given selector.

        Args:
            page (playwright.sync_api.Page): The active browser page.
            selector (str): The CSS selector to target.

        Returns:
            str: Cleaned text or 'Not found' if the element is missing.
        """
        try:
            element = page.locator(selector).first
            return element.inner_text().strip() if element.is_visible() else "Not found"
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to read selector {selector}: {e}")
            return "Not found"
