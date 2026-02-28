"""
ai/writer.py
Logic for generating tailored resumes/cover letters and parsing Job Descriptions using Gemini AI.
Includes automatic API key rotation and unique job hashing for deduplication.
"""

import os
import json
import asyncio
import re
from google import genai
from dotenv import load_dotenv
from assets.prompts import SYSTEM_PROMPT
from core.key_manager import KeyManager
from core.utils import generate_job_hash

load_dotenv()


class AIWriter:
    def __init__(self):
        """Initializes the AIWriter with KeyManager and API configuration."""
        self.key_mgr = KeyManager()
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
        self.resume_path = "assets/resume.txt"
        # Initialize the first client
        self._update_client()

    def _update_client(self):
        """Updates the Google GenAI client with the current active key from KeyManager."""
        api_key = self.key_mgr.get_current_key()
        if not api_key:
            raise ValueError("❌ No valid GEMINI_API_KEY found in KeyManager.")
        self.client = genai.Client(api_key=api_key)

    def process_application(self, job_description, job_title, company):
        """
        Generates tailored content via Gemini. Rotates API keys on quota limits (429).
        Returns a dictionary containing the job_hash and generated content.
        """
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"❌ Resume not found at {self.resume_path}")

        # Generate the unique hash for this specific job posting
        job_hash = generate_job_hash(company, job_title, job_description)

        with open(self.resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        full_prompt = SYSTEM_PROMPT.format(
            job_title=job_title,
            company=company,
            job_description=job_description,
            resume_text=resume_text
        )

        # Loop to attempt generation with available API keys
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

                # Clean JSON response from Markdown code blocks
                clean_text = response.text.strip()
                if clean_text.startswith("```"):
                    clean_text = re.sub(r'^```json\s*|```$', '', clean_text, flags=re.MULTILINE).strip()

                parsed_result = json.loads(clean_text)
                
                # Attach the hash to the result for synchronization/logging
                parsed_result["job_hash"] = job_hash
                return parsed_result

            except Exception as e:
                error_msg = str(e).lower()
                # Check for rate limits (429), quota exhaustion, or service limits
                if any(x in error_msg for x in ["429", "quota", "limit"]):
                    if self.key_mgr.rotate():
                        self._update_client()  # Swap key and update client
                        continue  # Retry with the new key
                    else:
                        print("🚨 All API keys in the pool have been exhausted.")
                        raise e

                print(f"⚠️ AI Generation Error: {e}")
                raise e
            finally:
                loop.close()