# Main Module: Orchestrates the scraping and AI workflow
from ai.writer import AIWriter
from core.file_manager import JobFileManager
from scrapers.factory import ScraperFactory # Importa a Fábrica


def main():
    writer = AIWriter()
    manager = JobFileManager()

    # Agora você só cola o Link!
    url = input("Cole o link da vaga do LinkedIn: ")

    try:
        # A Fábrica decide qual scraper usar
        scraper = ScraperFactory.get_scraper(url)
        job_data = scraper.get_job_data(url)

        print(f"🚀 IA processando para {job_data['title']} na {job_data['company']}...")
        results = writer.process_application(job_data['description'], job_data['title'], job_data['company'])

        manager.save_all(job_data, results)
        print("✅ Processo concluído com sucesso!")

    except Exception as e:
        print(f"❌ Falha no processo: {e}")


if __name__ == "__main__":
    main()
