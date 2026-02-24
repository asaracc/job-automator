import os
from dotenv import load_dotenv

load_dotenv()


class KeyManager:
    def __init__(self):
        """Inicializa o gestor processando o .env linha por linha."""
        raw_data = os.getenv("GEMINI_API_KEYS", "")
        self.keys = self._clean_keys(raw_data)
        self.current_index = 0

        if not self.keys:
            raise ValueError("❌ Nenhuma chave válida encontrada. Verifique o nome GEMINI_API_KEYS no .env.")

        print(f"🔑 KeyManager: {len(self.keys)} tokens carregados individualmente.")

    def _clean_keys(self, raw_string):
        """Lógica de processamento linha a linha para garantir isolamento das chaves."""
        keys_list = []
        # Divide a string em linhas reais
        for line in raw_string.splitlines():
            # Remove aspas, vírgulas e espaços de cada linha
            clean_key = line.replace('"', '').replace("'", "").replace(",", "").strip()
            if clean_key:
                keys_list.append(clean_key)
        return keys_list

    def get_current_key(self):
        """Retorna a chave atual para o cabeçalho da requisição."""
        return self.keys[self.current_index]

    def rotate(self):
        """Alterna para o próximo token disponível. Retorna False se esgotar."""
        if self.current_index + 1 < len(self.keys):
            self.current_index += 1
            hint = self.get_current_key()[:6]
            print(f"🔄 Rotação: Usando chave #{self.current_index + 1} ({hint}...)")
            return True
        return False
