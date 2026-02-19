# AI Writer: Logic for generating cover letters and parsing JDs
# ai/writer.py
import os
import json
import asyncio
from google import genai
from dotenv import load_dotenv
from assets.prompts import SYSTEM_PROMPT  # Importando seu novo prompt

load_dotenv()


class AIWriter:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
        self.resume_path = "assets/resume.txt"

    def process_application(self, job_description, job_title, company):
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"❌ Resume not found at {self.resume_path}")

        with open(self.resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        # Monta o prompt usando a variável externa
        full_prompt = SYSTEM_PROMPT.format(
            job_title=job_title,
            company=company,
            job_description=job_description,
            resume_text=resume_text
        )

        # CRÍTICO: Isola o loop de eventos para não colidir com o Playwright
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Função interna para chamar a IA
            def call_gemini():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config={'response_mime_type': 'application/json'}
                )

            # Executa a chamada em uma thread segura para o asyncio
            response = loop.run_until_complete(asyncio.to_thread(call_gemini))

            clean_text = response.text.strip()

            # Limpeza de blocos Markdown (```json ...)
            if clean_text.startswith("```"):
                clean_text = clean_text.split("json")[-1].split("```")[0].strip()

            return json.loads(clean_text)

        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao decodificar JSON: {e}")
            raise ValueError("A IA retornou um formato inválido.")
        except Exception as e:
            print(f"⚠️ AI Generation Error: {e}")
            raise e
        finally:
            loop.close()  # Sempre fecha o loop local
