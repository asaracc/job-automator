"""
core/utils.py
Centralized utilities for the Job Application Automator.
Contains the primary hashing logic used for deduplication across the project.
"""

import hashlib


def generate_job_hash(company, job_title, job_description):
    """
    Generates a unique SHA-256 hash for a job posting.
    Standardizes inputs to ensure the hash is deterministic and consistent.
    """
    # Force string conversion and normalization
    c = str(company).lower().strip()
    t = str(job_title).lower().strip()
    d = str(job_description).lower().strip()

    data_to_hash = f"{c}|{t}|{d}"
    return hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
