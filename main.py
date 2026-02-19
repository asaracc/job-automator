# Main Module: Orchestrates the scraping and AI workflow
import sys
from concurrent.futures import ThreadPoolExecutor
from ai.writer import AIWriter
from core.file_manager import JobFileManager
from scrapers.linkedin import LinkedInScraper


def main():
    # 1. Inicialização dos componentes
    writer = AIWriter()
    manager = JobFileManager()
    scraper = LinkedInScraper()

    # Este executor é o segredo: ele isola a IA em uma thread separada
    # resolvendo o erro de "asyncio loop"
    executor = ThreadPoolExecutor(max_workers=1)

    print("🚀 Gerador de Candidaturas Automático iniciado.")

    # 2. Entrada da URL de busca do LinkedIn
    search_url = input("Cole a URL da sua busca filtrada do LinkedIn: ").strip()

    if not search_url:
        print("❌ URL inválida.")
        return

    try:
        # 3. Início do Loop de Scraping
        # O scraper vai pausar para você logar e depois começar a 'yield' os dados
        for job_data in scraper.scrape_search_results(search_url):

            if not job_data.get('description') or job_data['description'] == "Não encontrado":
                print(f"⏭️ Pulando '{job_data['title']}': Descrição vazia.")
                continue

            print(f"\n[Processando] {job_data['title']} @ {job_data['company']}")

            try:
                print("   🤖 IA está analisando e gerando documentos (em thread isolada)...")

                # 4. EXCUÇÃO ISOLADA: Enviamos a tarefa para o executor
                future = executor.submit(
                    writer.process_application, 
                    job_data['description'], 
                    job_data['title'], 
                    job_data['company']
                )

                # O .result() aguarda a IA terminar sem travar o loop do Playwright
                results = future.result() 

                # 5. Salvamento dos arquivos
                manager.save_all(job_data, results)
                print(f"   ✅ Sucesso! Arquivos salvos para esta vaga.")

            except Exception as e:
                print(f"   ❌ Erro ao processar esta vaga com a IA: {e}")
                continue

        print("\n" + "="*50)
        print("🏁 Maratona concluída com sucesso!")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Falha crítica no sistema: {e}")
    finally:
        # Fecha o executor de threads de forma limpa
        executor.shutdown(wait=True)


if __name__ == "__main__":
    main()
