# sync_utils.py
import os
import sys
import json
import re
import pandas as pd
from dotenv import load_dotenv
from core.pdf_generator import PDFGenerator

# Garante que as variáveis do .env sejam carregadas
load_dotenv()

def clean_name(text):
    """Remove caracteres especiais e espaços duplos para nomes de arquivos."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text.replace(" ", "_").replace("__", "_")

def sync_all_from_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"❌ Erro: A pasta '{folder_path}' não existe.")
        return

    # 1. Carregar metadata e configurações
    metadata_path = os.path.join(folder_path, "metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ Erro: metadata.json não encontrado.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        local_metadata = json.load(f)
    
    app_id = local_metadata["application_meta"]["id"]
    job_title = local_metadata["job_info"]["title"]
    company = local_metadata["job_info"]["company"]
    user_name = os.getenv("USER_FULL_NAME", "Candidato") # Busca do .env
    
    master_csv = "applications_master_log.csv"

    # 2. Ler os conteúdos atuais dos arquivos MD
    sync_map = {
        "2_tailored_resume.md": ("resume_markdown", "resume_content_md", "Resume"),
        "3_cover_letter.md": ("cover_letter_markdown", "cover_letter_md", "Cover_Letter")
    }
    
    updated_contents = {}
    any_changes = False

    for filename, (json_key, csv_col, doc_type) in sync_map.items():
        md_path = os.path.join(folder_path, filename)
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                updated_contents[doc_type] = content
                
            if local_metadata["generated_content"].get(json_key) != content:
                local_metadata["generated_content"][json_key] = content
                any_changes = True

    # 3. Salvar atualizações (JSON e CSV)
    if any_changes:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(local_metadata, f, indent=4, ensure_ascii=False)
        
        if os.path.exists(master_csv):
            df = pd.read_csv(master_csv)
            if app_id in df['app_id'].values:
                df.loc[df['app_id'] == app_id, "resume_content_md"] = local_metadata["generated_content"]["resume_markdown"]
                df.loc[df['app_id'] == app_id, "cover_letter_md"] = local_metadata["generated_content"]["cover_letter_markdown"]
                df.to_csv(master_csv, index=False, encoding='utf-8')
                print("   ✅ JSON e CSV Master atualizados.")

# 4. Gerar PDFs (Deixando o PDFGenerator cuidar do prefixo do nome)
    pdf_gen = PDFGenerator()
    
    # Limpamos apenas a empresa e o cargo para o sufixo
    f_company = clean_name(company)
    f_job = clean_name(job_title)
    
    print(f"📄 Atualizando PDFs...")
    for doc_type, content in updated_contents.items():
        # Passamos apenas o "miolo" do nome. 
        # O PDFGenerator adicionará o USER_FULL_NAME automaticamente.
        suffix_filename = f"{doc_type}_{f_company}_{f_job}"
        
        try:
            # O PDFGenerator internamente fará: user_name + "_" + suffix_filename
            pdf_gen.convert_resume(content, suffix_filename, folder_path)
            # Para o print ficar bonito, pegamos o nome do candidato do env
            full_print_name = f"{os.getenv('USER_FULL_NAME', 'Candidato').replace(' ', '_')}_{suffix_filename}"
            print(f"   ✅ Sucesso: {full_print_name}.pdf")
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar {doc_type}: {e}")
    
    # Formatando partes do nome do arquivo
    f_user = clean_name(user_name)
    f_company = clean_name(company)
    f_job = clean_name(job_title)
    
    print(f"📄 Gerando PDFs para: {user_name}")
    for doc_type, content in updated_contents.items():
        # Nome sugerido: Nome_Candidato_Resume_Empresa_Cargo.pdf
        full_filename = f"{f_user}_{doc_type}_{f_company}_{f_job}"
        
        try:
            pdf_gen.convert_resume(content, full_filename, folder_path)
            print(f"   ✅ Sucesso: {full_filename}.pdf")
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar {doc_type}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python sync_utils.py <caminho_da_pasta>")
    else:
        sync_all_from_folder(sys.argv[1])