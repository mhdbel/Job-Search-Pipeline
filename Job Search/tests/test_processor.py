import unittest
import logging
from Job_Search.src.processor import (
    clean_data,
    normalize_text,
    create_job_fingerprint,
    generate_embeddings,
    index_jobs_in_faiss
)

# Configure logging to be quiet during tests
logging.basicConfig(level=logging.CRITICAL)

class TestProcessor(unittest.TestCase):

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  Software   Engineer  "), "software engineer")
        self.assertEqual(normalize_text("DATA SCIENTIST"), "data scientist")
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "")  # Assuming None should return empty string
        self.assertEqual(normalize_text(123), "")    # Assuming non-str should return empty string

    def test_create_job_fingerprint(self):
        job1 = {'title': 'Software Engineer', 'company': 'Tech Corp'}
        self.assertEqual(create_job_fingerprint(job1), ('software engineer', 'tech corp'))

        job2 = {'title': '  Software Engineer  ', 'company': 'tech corp', 'location': 'NY'}
        self.assertEqual(create_job_fingerprint(job2), ('software engineer', 'tech corp'))
        
        job3 = {'title': 'Software Engineer'}
        self.assertEqual(create_job_fingerprint(job3), ('software engineer', ''))  # Missing company

        job4 = {}
        self.assertEqual(create_job_fingerprint(job4), ('', ''))  # Empty job

    def test_clean_data_empty_list(self):
        self.assertEqual(clean_data([]), [])

    def test_clean_data_no_duplicates(self):
        jobs = [
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1'},
            {'title': 'Data Scientist', 'company': 'Data Inc', 'link': 'link2'}
        ]
        self.assertEqual(clean_data(jobs), jobs)

    def test_clean_data_with_duplicates(self):
        jobs = [
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1a'},
            {'title': 'Data Scientist', 'company': 'Data Inc', 'link': 'link2'},
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1b'},  # Duplicate by fingerprint
            {'title': 'software engineer', 'company': 'TECH CORP', 'link': 'link1c'}  # Duplicate by fingerprint (normalized)
        ]
        expected = [
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1a'},
            {'title': 'Data Scientist', 'company': 'Data Inc', 'link': 'link2'}
        ]
        cleaned = clean_data(jobs)
        self.assertEqual(len(cleaned), 2)
        self.assertTrue(any(j['link'] == 'link1a' for j in cleaned))
        self.assertTrue(any(j['link'] == 'link2' for j in cleaned))

    def test_clean_data_missing_essential_fields(self):
        jobs = [
            {'title': 'Good Job', 'company': 'Good Co', 'link': 'good_link'},
            {'title': 'No Link Job', 'company': 'Bad Co'},
            {'company': 'No Title Job', 'link': 'bad_link2'},
            {'title': 'No Company Job', 'link': 'bad_link3'}
        ]
        expected = [
            {'title': 'Good Job', 'company': 'Good Co', 'link': 'good_link'}
        ]
        with self.assertLogs(logger='Job_Search.src.processor', level='WARNING') as cm:
            self.assertEqual(clean_data(jobs), expected)
            self.assertTrue(any("Skipping job with missing essential fields" in log_msg for log_msg in cm.output))

    def test_clean_data_input_not_list(self):
        with self.assertLogs(logger='Job_Search.src.processor', level='ERROR') as cm:
            result = clean_data("not a list")
            self.assertEqual(result, [])
            self.assertTrue(any("expects a list of job data" in log_msg for log_msg in cm.output))

    def test_clean_data_list_contains_non_dict(self):
        jobs = [
            {'title': 'Valid Job', 'company': 'Good Co', 'link': 'link1'},
            "not a job dict",
            12345
        ]
        expected = [
            {'title': 'Valid Job', 'company': 'Good Co', 'link': 'link1'}
        ]
        with self.assertLogs(logger='Job_Search.src.processor', level='WARNING') as cm:
            result = clean_data(jobs)
            self.assertEqual(result, expected)
            self.assertTrue(any("Skipping non-dictionary item" in log_msg for log_msg in cm.output))

    # New Tests for Embedding Generation
    def test_generate_embeddings(self):
        jobs = [
            {"title": "Python Developer", "description": "We are looking for a Python developer..."},
            {"title": "Data Scientist", "description": "Seeking a data scientist with expertise in ML..."}
        ]
        descriptions = [job["description"] for job in jobs]
        embeddings = generate_embeddings(jobs)

        # Validate shape of embeddings
        self.assertEqual(embeddings.shape[0], len(jobs))  # Number of embeddings matches number of jobs
        self.assertEqual(embeddings.shape[1], 384)  # Dimensionality of embeddings (all-MiniLM-L6-v2)

    # New Tests for FAISS Indexing
    def test_index_jobs_in_faiss(self):
        jobs = [
            {"title": "Python Developer", "description": "We are looking for a Python developer..."},
            {"title": "Data Scientist", "description": "Seeking a data scientist with expertise in ML..."}
        ]
        index, job_metadata = index_jobs_in_faiss(jobs)

        # Validate FAISS index
        self.assertEqual(index.ntotal, len(jobs))  # Number of indexed items matches number of jobs

        # Validate job metadata
        self.assertEqual(len(job_metadata), len(jobs))
        self.assertIn(0, job_metadata)  # Check if job metadata contains indices as keys
        self.assertEqual(job_metadata[0]["title"], "Python Developer")

if __name__ == '__main__':
    unittest.main()
