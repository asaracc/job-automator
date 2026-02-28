"""
tests/test_hashing.py
Unit tests to validate the integrity and consistency of the job hashing logic.
"""

import unittest
from core.utils import generate_job_hash


class TestJobHasher(unittest.TestCase):
    def setUp(self):
        """Standard mock data for testing."""
        self.company = "Google"
        self.title = "Software Engineer"
        self.desc = "We are looking for a Python expert..."

    def test_determinism(self):
        """Test that the same input always produces the exact same hash."""
        hash1 = generate_job_hash(self.company, self.title, self.desc)
        hash2 = generate_job_hash(self.company, self.title, self.desc)
        self.assertEqual(hash1, hash2, "❌ Determinism Failed: Identical inputs produced different hashes.")

    def test_case_insensitivity(self):
        """Test that casing does not change the hash (Google == google)."""
        hash_upper = generate_job_hash("GOOGLE", "ENGINEER", self.desc)
        hash_lower = generate_job_hash("google", "engineer", self.desc)
        self.assertEqual(hash_upper, hash_lower, "❌ Case Sensitivity Error: Hashes should be case-insensitive.")

    def test_whitespace_tolerance(self):
        """Test that leading/trailing spaces are ignored."""
        hash_clean = generate_job_hash("Apple", "Dev", "Description")
        hash_dirty = generate_job_hash(" Apple ", " Dev ", " Description \n")
        self.assertEqual(hash_clean, hash_dirty, "❌ Whitespace Error: Hashes should ignore surrounding spaces/newlines.")

    def test_sensitivity(self):
        """Test that a tiny change in description results in a completely different hash."""
        hash1 = generate_job_hash(self.company, self.title, "Working with Python")
        hash2 = generate_job_hash(self.company, self.title, "Working with Python.") # Added a period
        self.assertNotEqual(hash1, hash2, "❌ Sensitivity Failed: Tiny change did not trigger a new hash.")

    def test_empty_fields(self):
        """Test that the function handles empty strings or None without crashing."""
        try:
            generate_job_hash("", None, "Valid Description")
        except Exception as e:
            self.fail(f"❌ Robustness Failed: Function crashed on empty/None input: {e}")

if __name__ == "__main__":
    unittest.main()