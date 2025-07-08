import unittest
import logging
from Job_Search.src.analyzer import analyze_jobs, hybrid_search  # Updated imports
from Job_Search.src.processor import clean_data, index_jobs_in_faiss  # For indexing jobs

# Configure logging to be quiet during tests, unless specifically needed for a test
logging.basicConfig(level=logging.CRITICAL)

class TestAnalyzer(unittest.TestCase):

    def test_analyze_jobs_empty_list(self):
        """Test analyze_jobs with an empty list of jobs."""
        self.assertEqual(analyze_jobs([]), [])

    def test_analyze_jobs_no_interesting_jobs(self):
        """Test with jobs that don't meet the 'interesting' criteria."""
        jobs = [
            {'title': 'Senior Developer', 'company': 'Tech Corp', 'applicants': 15, 'id': 'job1'},
            {'title': 'Project Manager', 'company': 'Biz Inc', 'applicants': 20, 'id': 'job2'}
        ]
        self.assertEqual(analyze_jobs(jobs), [])

    def test_analyze_jobs_with_interesting_jobs(self):
        """Test with some jobs meeting the 'interesting' criteria (applicants < 10)."""
        jobs = [
            {'title': 'Junior Developer', 'company': 'Startup LLC', 'applicants': 5, 'id': 'job3'},
            {'title': 'Senior Developer', 'company': 'Tech Corp', 'applicants': 15, 'id': 'job1'},
            {'title': 'Data Analyst', 'company': 'Data Co', 'applicants': 8, 'id': 'job4'}
        ]
        expected_interesting_jobs = [
            {'title': 'Junior Developer', 'company': 'Startup LLC', 'applicants': 5, 'id': 'job3'},
            {'title': 'Data Analyst', 'company': 'Data Co', 'applicants': 8, 'id': 'job4'}
        ]
        self.assertEqual(analyze_jobs(jobs), expected_interesting_jobs)

    def test_analyze_jobs_missing_applicants_key(self):
        """Test jobs where the 'applicants' key is missing (should default to 0)."""
        jobs = [
            {'title': 'Intern', 'company': 'Big Firm', 'id': 'job5'},  # Missing 'applicants'
            {'title': 'Senior Developer', 'company': 'Tech Corp', 'applicants': 15, 'id': 'job1'}
        ]
        # The intern job (default applicants 0) should be considered interesting.
        expected_interesting_jobs = [
            {'title': 'Intern', 'company': 'Big Firm', 'id': 'job5'}
        ]
        self.assertEqual(analyze_jobs(jobs), expected_interesting_jobs)

    def test_analyze_jobs_non_integer_applicants(self):
        """Test jobs with non-integer 'applicants' values."""
        jobs = [
            {'title': 'QA Tester', 'company': 'Test Inc', 'applicants': 'few', 'id': 'job6'},
            {'title': 'Designer', 'company': 'Creative Co', 'applicants': None, 'id': 'job7'},
            {'title': 'Developer', 'company': 'Code LLC', 'applicants': 3, 'id': 'job8'}
        ]
        # Based on current analyzer.py, 'few' and None for applicants will lead to using default 0,
        # thus making them 'interesting'.
        expected_interesting_jobs = [
            {'title': 'QA Tester', 'company': 'Test Inc', 'applicants': 'few', 'id': 'job6'},
            {'title': 'Designer', 'company': 'Creative Co', 'applicants': None, 'id': 'job7'},
            {'title': 'Developer', 'company': 'Code LLC', 'applicants': 3, 'id': 'job8'}
        ]
        # Suppress warnings from the logger during this specific test if they are expected
        with self.assertLogs(logger='Job_Search.src.analyzer', level='WARNING') as cm:
            result = analyze_jobs(jobs)
            self.assertEqual(result, expected_interesting_jobs)
            # Check that warnings were logged for non-integer applicants
            self.assertTrue(any("non-integer applicants value 'few'" in log_msg for log_msg in cm.output))
            self.assertTrue(any("non-integer applicants value 'None'" in log_msg for log_msg in cm.output))

    def test_analyze_jobs_input_not_list(self):
        """Test analyze_jobs with input that is not a list."""
        with self.assertLogs(logger='Job_Search.src.analyzer', level='ERROR') as cm:
            result = analyze_jobs("not a list")
            self.assertEqual(result, [])
            self.assertTrue(any("expects a list of jobs" in log_msg for log_msg in cm.output))

    def test_analyze_jobs_list_contains_non_dict(self):
        """Test analyze_jobs with a list containing non-dictionary items."""
        jobs = [
            {'title': 'Valid Job', 'company': 'Good Co', 'applicants': 5, 'id': 'job9'},
            "not a job dict",
            12345
        ]
        expected_interesting_jobs = [
            {'title': 'Valid Job', 'company': 'Good Co', 'applicants': 5, 'id': 'job9'}
        ]
        with self.assertLogs(logger='Job_Search.src.analyzer', level='WARNING') as cm:
            result = analyze_jobs(jobs)
            self.assertEqual(result, expected_interesting_jobs)
            self.assertTrue(any("Skipping non-dictionary job item" in log_msg for log_msg in cm.output))

    # New Tests for Hybrid Search
    def test_hybrid_search_retrieves_relevant_jobs(self):
        """Test hybrid search retrieves relevant jobs based on a query."""
        jobs = [
            {"title": "Python Developer", "company": "Company A", "description": "We are looking for a Python developer...", "link": "https://example.com/job/123 "},
            {"title": "Data Scientist", "company": "Company B", "description": "Seeking a data scientist with expertise in ML...", "link": "https://example.com/job/456 "}
        ]

        # Clean and index jobs
        cleaned_jobs = clean_data(jobs)
        index, job_metadata = index_jobs_in_faiss(cleaned_jobs)

        # Perform hybrid search
        query = "Find me remote Python developer jobs."
        relevant_jobs = hybrid_search(query, cleaned_jobs, index, top_k=2)

        # Validate results
        self.assertEqual(len(relevant_jobs), 2)
        self.assertIn(relevant_jobs[0]["title"], ["Python Developer", "Data Scientist"])
        self.assertIn(relevant_jobs[1]["title"], ["Python Developer", "Data Scientist"])

    def test_hybrid_search_handles_empty_query(self):
        """Test hybrid search handles an empty or irrelevant query gracefully."""
        jobs = [
            {"title": "Python Developer", "company": "Company A", "description": "We are looking for a Python developer...", "link": "https://example.com/job/123 "},
            {"title": "Data Scientist", "company": "Company B", "description": "Seeking a data scientist with expertise in ML...", "link": "https://example.com/job/456 "}
        ]

        # Clean and index jobs
        cleaned_jobs = clean_data(jobs)
        index, job_metadata = index_jobs_in_faiss(cleaned_jobs)

        # Perform hybrid search with an empty query
        query = ""
        relevant_jobs = hybrid_search(query, cleaned_jobs, index, top_k=2)

        # Validate results
        self.assertEqual(len(relevant_jobs), 0)

if __name__ == '__main__':
    unittest.main()
