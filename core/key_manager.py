import os
from dotenv import load_dotenv

# Garante que o .env seja carregado ao importar o módulo
load_dotenv()


class KeyManager:
    def __init__(self):
        """
        Inicializa o gestor de chaves processando a string do .env
        em uma lista (array) de strings limpas.
        """
        # 1. Busca a string bruta do .env
        raw_keys = os.getenv("GEMINI_API_KEYS", "")

        # 2. Processamento para transformar em Array:
        # - replace("\n", ""): Remove quebras de linha se você usou aspas no .env
        # - split(","): Divide a string em cada vírgula
        # - k.strip(): Remove espaços em branco ao redor de cada chave
        # - if k.strip(): Garante que não adicionaremos strings vazias na lista
        self.keys = [
            k.strip()
            for k in raw_keys.replace("\n", "").split(",")
            if k.strip()
        ]

        # Fallback: Se a lista estiver vazia, tenta a chave única antiga
        if not self.keys:
            single_key = os.getenv("GEMINI_API_KEY")
            if single_key:
                self.keys = [single_key.strip()]

        if not self.keys:
            raise ValueError("❌ Nenhuma chave API encontrada. Verifique seu arquivo .env.")

        self.current_index = 0

        # Log de inicialização (seguro)
        print(f"🔑 KeyManager: {len(self.keys)} tokens carregados com sucesso.")

    def get_current_key(self):
        """Retorna o token que está sendo usado no momento."""
        return self.keys[self.current_index]

    def rotate(self):
        """
        Move para o próximo token na lista.
        Retorna True se houver um novo token, False se todos esgotarem.
        """
        if self.current_index + 1 < len(self.keys):
            self.current_index += 1
            # Mostra apenas os 4 primeiros caracteres da nova chave por segurança
            new_key_hint = self.get_current_key()[:4] + "..."
            print(f"🔄 Limite de cota atingido. Alternando para chave #{self.current_index + 1} ({new_key_hint})")
            return True

        print("🚨 ERRO: Todas as chaves API disponíveis foram esgotadas!")
        return False
