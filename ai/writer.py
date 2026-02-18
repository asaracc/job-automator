# AI Writer: Logic for generating cover letters and parsing JDs
import os
import json
import re
from google import genai  # Corrected Import
from dotenv import load_dotenv

load_dotenv()


class AIWriter:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
            
        # Corrected Initialization for the new SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL_NAME")
        self.resume_path = "assets/resume.txt"

    def process_application(self, job_description, job_title, company):
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"❌ Resume not found at {self.resume_path}")

        with open(self.resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        prompt = f"""
        Act as an expert ATS recruiter. Target Role: {job_title} at {company}.
        
        STEP 1: DATA EXTRACTION
        Extract the following fields from the Job Description. If not found, write "Not Listed".
        - Salary: Look for hourly or annual ranges.
        - Country: The primary country of the role.
        - Work Model: Remote, Hybrid, or On-Site.
        - Benefits: List key perks (401k, Health, etc.).

        STRICT RULES FOR RESUME REWRITE:
        1. DO NOT DELETE ANY WORK EXPERIENCE. Every role in the original resume must remain.
        2. TAILOR THROUGH EMPHASIS: For relevant roles, expand the bullet points to match the JD keywords.
        3. CONDENSE FOR SPACE: For older or less relevant roles, keep them but reduce them to 1-2 bullet points.
        4. MAINTAIN CHRONOLOGY: Keep the 15+ years of experience intact so the career timeline is clear.

        FACT INTEGRITY RULES:
        1. DO NOT INVENT ROLES: Use exactly the job titles and companies provided in the resume.
        2. DO NOT FABRICATE DATA: You may rephrase descriptions to highlight relevant skills, but you cannot claim the user did something they haven't.
        3. KEEP FULL HISTORY: All 15+ years must be present.

        SCORING RUBRIC:
        - 10/10: Only if they meet 100% of 'Required' and 'Preferred' skills.
        - 7/10: Meets all 'Required' but missing 'Preferred'.
        - 5/10: Missing key 'Required' skills. 
        - BE HONEST: If skills are missing, the score MUST reflect that.

        TASKS:
        1. Rate original resume (0-10).
        2. Rewrite resume to be as close as possible to 10/10 match using the rules above.
        3. Rate tailored version (0-10).
        4. List specific skill GAPS.
        5. Write a cover letter in Markdown.
        6. Brief fit analysis.

        OUTPUT ONLY VALID JSON:
        Act as a Senior Technical Recruiter. You must generate a JSON response following this EXACT structure:
        {{
            "metadata": {{ "salary": "", "country": "", "work_model": "", "benefits": "" }},
            "scores": {{ "original": 0, "tailored": 0 }},
            "analysis": {{ "fit_report": "", "gaps": [] }},
            "files": {{ "tailored_resume_md": "", "cover_letter_md": "" }}
        }}
        RULES:
        1. Extract salary/country/model/benefits from JD.
        2. Audit Resume vs JD (strict score).
        3. Rewrite Resume: Keep all 15+ years. No inventions.
        4. Write Cover Letter.
        
        JD: {job_description}
        Resume: {resume_text}
        """
        
        try:
            # Corrected generation call for the new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_match:
                raise ValueError("AI did not return a valid JSON block")
                
            return json.loads(json_match.group())
        except Exception as e:
            print(f"⚠️ AI Generation Error: {e}")
            raise e