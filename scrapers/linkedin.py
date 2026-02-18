from playwright.sync_api import sync_playwright
import time

class LinkedInScraper:
    def get_job_data(self, url: str):
        print(f"🌐 Acessando LinkedIn: {url}")
        
        with sync_playwright() as p:
            # Lançamos o navegador (headless=False ajuda a debugar e evitar blocks)
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page()
            
            # Definir um User-Agent real para evitar ser bloqueado de cara
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            page.goto(url)
            
            # Aguarda o conteúdo principal carregar
            # O LinkedIn às vezes pede login se você acessar muitas vezes
            try:
                page.wait_for_selector(".top-card-layout__title", timeout=10000)
            except:
                print("⚠️ Aviso: O seletor demorou a carregar. Verifique se há CAPTCHA.")

            # Extração dos dados usando seletores comuns do LinkedIn (2026)
            data = {
                "title": self._get_text(page, "h1.top-card-layout__title"),
                "company": self._get_text(page, "a.topcard__org-name-link"),
                "description": self._get_text(page, ".description__text"),
                "url": url
            }
            
            browser.close()
            return data

    def _get_text(self, page, selector):
        try:
            return page.locator(selector).inner_text().strip()
        except:
            return "Não encontrado"