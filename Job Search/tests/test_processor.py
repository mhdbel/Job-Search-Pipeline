import unittest
import logging
from Job_Search.src.processor import clean_data, normalize_text, create_job_fingerprint

# Configure logging to be quiet during tests
logging.basicConfig(level=logging.CRITICAL)

class TestProcessor(unittest.TestCase):

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  Software   Engineer  "), "software engineer")
        self.assertEqual(normalize_text("DATA SCIENTIST"), "data scientist")
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "") # Assuming None should return empty string
        self.assertEqual(normalize_text(123), "")    # Assuming non-str should return empty string

    def test_create_job_fingerprint(self):
        job1 = {'title': 'Software Engineer', 'company': 'Tech Corp'}
        self.assertEqual(create_job_fingerprint(job1), ('software engineer', 'tech corp'))

        job2 = {'title': '  Software Engineer  ', 'company': 'tech corp', 'location': 'NY'}
        self.assertEqual(create_job_fingerprint(job2), ('software engineer', 'tech corp'))
        
        job3 = {'title': 'Software Engineer'}
        self.assertEqual(create_job_fingerprint(job3), ('software engineer', '')) # Missing company

        job4 = {}
        self.assertEqual(create_job_fingerprint(job4), ('', '')) # Empty job

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
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1b'}, # Duplicate by fingerprint
            {'title': 'software engineer', 'company': 'TECH CORP', 'link': 'link1c'}  # Duplicate by fingerprint (normalized)
        ]
        expected = [
            {'title': 'Software Engineer', 'company': 'Tech Corp', 'link': 'link1a'},
            {'title': 'Data Scientist', 'company': 'Data Inc', 'link': 'link2'}
        ]
        # The fingerprinting logic uses normalized title and company. 
        # The first unique fingerprint encountered is kept.
        cleaned = clean_data(jobs)
        self.assertEqual(len(cleaned), 2)
        # Check if the kept jobs are among the expected ones (order might vary depending on exact dict contents)
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

if __name__ == '__main__':
    unittest.main()
