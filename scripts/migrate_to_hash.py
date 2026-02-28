"""
scripts/migrate_to_hash.py
Migration script to update the master log using the centralized hashing function.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from core.utils import generate_job_hash

# Add the project root to sys.path so we can import from 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

MASTER_CSV = "applications_master_log.csv"


def run_migration():
    """Consistent extraction using the imported centralized hash function."""
    if not os.path.exists(MASTER_CSV):
        print(f"❌ Error: {MASTER_CSV} not found.")
        return

    df = pd.read_csv(MASTER_CSV)

    if 'job_hash' in df.columns:
        df = df.drop(columns=['job_hash'])

    hashes = []
    for _, row in df.iterrows():
        # Using the imported function
        new_hash = generate_job_hash(
            row.get('company', 'unknown'),
            row.get('title', 'unknown'),
            row.get('job_description', 'unknown')
        )
        hashes.append(new_hash)

    df.insert(0, 'job_hash', hashes)

    # Backup and Save
    os.replace(MASTER_CSV, f"{MASTER_CSV}.bak")
    df.to_csv(MASTER_CSV, index=False, encoding='utf-8')
    print(f"🚀 Migration complete! {len(df)} rows processed via core.utils.")


if __name__ == "__main__":
    run_migration()
