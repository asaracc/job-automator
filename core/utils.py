import hashlib


def generate_job_hash(company, job_title, job_description):
    """
    Gera um ID único baseado nas informações da vaga.
    Remove espaços e converte para minúsculas para evitar variações bobas.
    """
    # 1. Normalizamos os dados para que "Google" e "google" gerem o mesmo ID
    raw_string = f"{company.lower()}|{job_title.lower()}|{job_description.strip()}"

    # 2. Geramos o hash SHA-256
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
