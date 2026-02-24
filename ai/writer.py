# AI Writer: Logic for generating cover letters and parsing JDs
# ai/writer.py
import os
import json
import asyncio
import re
from google import genai
from dotenv import load_dotenv
from assets.prompts import SYSTEM_PROMPT
from core.key_manager import KeyManager  # Importando o gestor

load_dotenv()


class AIWriter:
    def __init__(self):
        self.key_mgr = KeyManager()
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
        self.resume_path = "assets/resume.txt"
        # Inicializa o primeiro cliente
        self._update_client()

    def _update_client(self):
        """Atualiza o cliente com a chave atual do KeyManager"""
        api_key = self.key_mgr.get_current_key()
        if not api_key:
            raise ValueError("❌ Nenhuma GEMINI_API_KEY encontrada.")
        self.client = genai.Client(api_key=api_key)

    def process_application(self, job_description, job_title, company):
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"❌ Resume not found at {self.resume_path}")

        with open(self.resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        full_prompt = SYSTEM_PROMPT.format(
            job_title=job_title,
            company=company,
            job_description=job_description,
            resume_text=resume_text
        )

        # Loop infinito para tentar as chaves disponíveis
        while True:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                def call_gemini():
                    return self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config={'response_mime_type': 'application/json'}
                    )

                response = loop.run_until_complete(asyncio.to_thread(call_gemini))

                clean_text = response.text.strip()
                if clean_text.startswith("```"):
                    clean_text = re.sub(r'^```json\s*|```$', '', clean_text, flags=re.MULTILINE).strip()

                return json.loads(clean_text)

            except Exception as e:
                error_msg = str(e).lower()
                # Verifica se o erro é de cota/limite (429 ou Quota Exceeded)
                if "429" in error_msg or "quota" in error_msg or "limit" in error_msg:
                    if self.key_mgr.rotate():
                        self._update_client()  # Troca a chave no cliente do Google
                        continue  # Tenta novamente o loop com a nova chave
                    else:
                        print("🚨 Todas as chaves API foram esgotadas.")
                        raise e

                print(f"⚠️ AI Generation Error: {e}")
                raise e
            finally:
                loop.close()
