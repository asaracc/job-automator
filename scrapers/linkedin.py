"""
scrapers/linkedin.py
Module for automated LinkedIn job data extraction using Playwright.
Handles session persistence, lazy loading, and data mapping.
"""

import time
from playwright.sync_api import sync_playwright


class LinkedInScraper:
    """
    A scraper class to navigate LinkedIn search results and extract job details.

    Attributes:
        selectors (dict): CSS selectors for various job page elements.
    """

    def __init__(self):
        """Initializes the scraper with updated 2026 CSS selectors."""
        self.selectors = {
            "job_card": ".scaffold-layout__list-item",
            "title": ".job-details-jobs-unified-top-card__job-title",
            "company": ".job-details-jobs-unified-top-card__company-name",
            "description": ".jobs-description__content",
            "left_container": ".jobs-search-results-list"
        }

    def scrape_search_results(self, search_url):
        """
        Navigates to the search URL and yields job data dictionaries.

        Args:
            search_url (str): The filtered LinkedIn job search URL.

        Yields:
            dict: Contains 'title', 'company', 'description', and 'url'.
        """
        with sync_playwright() as p:
            # Persistent context saves login cookies in ./playwright_data
            user_data_dir = "./playwright_data"
            browser = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                slow_mo=600,
                args=["--start-maximized"]
            )

            page = browser.pages[0]
            page.goto(search_url)

            print("\n" + "=" * 60)
            print("🛠️  MANUAL PREPARATION MODE")
            print("1. Log in if required.")
            print("2. Apply your FILTERS now (Level, Date, Remote, etc.).")
            print("3. Once the list is correct, return to this terminal.")
            print("=" * 60 + "\n")

            input(">>> Filters adjusted? Press ENTER to start extraction...")

            # --- Step 1: Handle Lazy Loading ---
            print("\n⏳ Loading all jobs from the sidebar...")
            try:
                list_container = page.locator(self.selectors["left_container"])
                if list_container.count() > 0:
                    for _ in range(5):
                        list_container.evaluate("node => node.scrollTop += 1000")
                        time.sleep(1)
            except Exception as e:
                print(f"⚠️  Scroll Warning: {e}")

            # --- Step 2: Identify Job Cards ---
            page.wait_for_selector(self.selectors["job_card"], timeout=10000)
            cards = page.locator(self.selectors["job_card"]).all()

            print(f"🎯 Found {len(cards)} jobs matching your filters.")

            # --- Step 3: Extraction Loop ---
            for i, card in enumerate(cards):
                try:
                    print(f"   📄 Reading job {i+1}/{len(cards)}...")

                    card.scroll_into_view_if_needed()
                    card.click()
                    time.sleep(2)  # Wait for the detail pane to update

                    data = {
                        "title": self._get_text(page, self.selectors["title"]),
                        "company": self._get_text(page, self.selectors["company"]),
                        "description": self._get_text(page, self.selectors["description"]),
                        "url": page.url
                    }

                    # Fallback for dynamic description boxes
                    if not data["description"] or data["description"] == "unknown":
                        data["description"] = self._get_text(page, ".jobs-box__group")

                    yield data

                except Exception as e:
                    print(f"   ⚠️  Error extracting job {i+1}: {e}")
                    continue

            print("\n✅ Page scan complete.")
            browser.close()

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
            if element.is_visible():
                return element.inner_text().strip()
            return "Not found"
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to read selector {selector}: {e}")
            return "Not found"