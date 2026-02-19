import time
from playwright.sync_api import sync_playwright


class LinkedInScraper:
    def __init__(self):
        # Seletores atualizados para a interface do LinkedIn em 2026
        self.selectors = {
            "job_card": ".scaffold-layout__list-item",
            "title": ".job-details-jobs-unified-top-card__job-title",
            "company": ".job-details-jobs-unified-top-card__company-name",
            "description": ".jobs-description__content",
            "container_esquerda": ".jobs-search-results-list"
        }

    def scrape_search_results(self, search_url):
        with sync_playwright() as p:
            # Usa um diretório persistente para salvar cookies e não pedir login toda vez
            user_data_dir = "./playwright_data"
            browser = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                slow_mo=600,  # Velocidade humana para evitar detecção
                args=["--start-maximized"]
            )

            page = browser.pages[0]
            page.goto(search_url)

            print("\n" + "="*60)
            print("🛠️  MODO DE PREPARAÇÃO MANUAL")
            print("1. Realize o login se necessário.")
            print("2. Aplique seus FILTROS agora (Nível, Data, Remoto, etc.).")
            print("3. Quando a lista estiver correta, volte aqui.")
            print("="*60 + "\n")

            input(">>> Ajustou os filtros? Aperte ENTER para iniciar a extração...")

            # --- Passo 1: Scroll na lista da esquerda ---
            # O LinkedIn usa 'lazy loading'. Se não scrollar, ele só lê as primeiras 2 ou 3 vagas.
            print("⏳ Carregando todas as vagas da lista lateral...")
            try:
                # Tenta localizar o container da lista para fazer o scroll nele
                list_container = page.locator(self.selectors["container_esquerda"])
                if list_container.count() > 0:
                    for _ in range(5):  # Faz scroll 5 vezes para baixo
                        list_container.evaluate("node => node.scrollTop += 1000")
                        time.sleep(1)
            except Exception as e:
                print(f"⚠️ Aviso no scroll: {e}")

            # --- Passo 2: Mapear os Cards ---
            page.wait_for_selector(self.selectors["job_card"], timeout=10000)
            cards = page.locator(self.selectors["job_card"]).all()

            print(f"🎯 Total de {len(cards)} vagas encontradas com seus filtros.")

            # --- Passo 3: Loop de Extração ---
            for i, card in enumerate(cards):
                try:
                    print(f"   📄 Lendo vaga {i+1}/{len(cards)}...")

                    # Clica no card para abrir o detalhe na direita
                    card.scroll_into_view_if_needed()
                    card.click()
                    time.sleep(2)  # Espera carregar o painel da direita

                    # Extração dos dados
                    data = {
                        "title": self._get_text(page, self.selectors["title"]),
                        "company": self._get_text(page, self.selectors["company"]),
                        "description": self._get_text(page, self.selectors["description"]),
                        "url": page.url
                    }

                    # Se a descrição falhar, tenta um seletor alternativo genérico
                    if not data["description"] or data["description"] == "Não encontrado":
                        data["description"] = self._get_text(page, ".jobs-box__group")

                    yield data  # Envia para o main.py processar com a IA

                except Exception as e:
                    print(f"   ⚠️ Erro ao clicar na vaga {i+1}: {e}")
                    continue

            print("\n✅ Varredura da página concluída.")
            browser.close()

    def _get_text(self, page, selector):
        """Helper para extrair texto de forma segura"""
        try:
            element = page.locator(selector).first
            if element.is_visible():
                # Limpeza básica de excesso de espaços e quebras
                return element.inner_text().strip()
            return "Não encontrado"
        except Exception as e:
            # Capturamos exceções genéricas de software,
            # mas permitimos que sinais do sistema (Ctrl+C) passem.
            print(f"⚠️ Aviso: Falha ao ler seletor {selector}: {e}")
            return "Não encontrado"
