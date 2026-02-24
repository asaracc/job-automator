import os
import sys
import json
import re
import pandas as pd
from dotenv import load_dotenv
from core.pdf_generator import PDFGenerator

load_dotenv()


def clean_name(text):
    """Remove caracteres especiais e garante que não haja duplicatas de termos."""
    # Remove caracteres proibidos e transforma separadores em underscores
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = text.replace(" - ", "_").replace(" ", "_").replace("-", "_")
    # Remove underscores duplos e limpa as extremidades
    return re.sub(r'_+', '_', text).strip('_')


def sync_all_from_folder(folder_path):
    """Sincroniza arquivos Markdown com JSON/CSV e gera PDFs com nomenclatura limpa."""
    if not os.path.exists(folder_path):
        print(f"❌ Erro: A pasta '{folder_path}' não existe.")
        return

    # 1. Carregar metadata
    metadata_path = os.path.join(folder_path, "metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ Erro: metadata.json não encontrado.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        local_metadata = json.load(f)

    app_id = local_metadata["application_meta"]["id"]
    job_title = local_metadata["job_info"]["title"]
    company = local_metadata["job_info"]["company"]
    master_csv = "applications_master_log.csv"

    # 2. Mapeamento de arquivos para sincronização
    sync_map = {
        "2_tailored_resume.md": ("resume_markdown", "Resume"),
        "3_cover_letter.md": ("cover_letter_markdown", "Cover_Letter")
    }

    updated_contents = {}
    any_changes = False

    for filename, (json_key, doc_type) in sync_map.items():
        md_path = os.path.join(folder_path, filename)
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                updated_contents[doc_type] = content

            if local_metadata["generated_content"].get(json_key) != content:
                local_metadata["generated_content"][json_key] = content
                any_changes = True

    # 3. Salvar atualizações no JSON e CSV
    if any_changes:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(local_metadata, f, indent=4, ensure_ascii=False)

        if os.path.exists(master_csv):
            df = pd.read_csv(master_csv)
            if app_id in df['app_id'].values:
                df.loc[df['app_id'] == app_id, "resume_content_md"] = (
                    local_metadata["generated_content"]["resume_markdown"]
                )
                df.loc[df['app_id'] == app_id, "cover_letter_md"] = local_metadata["generated_content"].get(
                    "cover_letter_markdown", ""
                )
                df.to_csv(master_csv, index=False, encoding='utf-8')
                print("   ✅ Banco de Dados (JSON/CSV) sincronizado.")

    # 4. Geração de PDFs
    pdf_gen = PDFGenerator()
    f_company = clean_name(company)
    f_job = clean_name(job_title)

    # Evita duplicidade se o título da vaga já contiver o nome da empresa
    if f_job.lower().startswith(f_company.lower()):
        f_job = f_job[len(f_company):].strip('_')

    print("📄 Gerando Documentos...")
    for doc_type, content in updated_contents.items():
        # O PDFGenerator já adiciona o USER_FULL_NAME internamente.
        # Passamos apenas o sufixo: TipoDocumento_Empresa_Cargo
        suffix_filename = f"{doc_type}_{f_company}_{f_job}"

        try:
            pdf_gen.convert_resume(content, suffix_filename, folder_path)
            print(f"   ✅ Criado: ..._{suffix_filename}.pdf")
        except Exception as e:
            print(f"   ⚠️ Erro em {doc_type}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python sync_utils.py <caminho_da_pasta>")
    else:
        sync_all_from_folder(sys.argv[1])
