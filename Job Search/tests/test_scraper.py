import unittest
from unittest.mock import patch, mock_open, MagicMock
import yaml
import os
from Job_Search.src.scraper import load_config, scrape_job_board, scrape_jobs

# Determine the project root for test purposes, assuming tests are in Job_Search/tests/
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_FOR_TESTS = os.path.dirname(TEST_DIR)  # This should be 'Job_Search/'

# This is the path that scraper.py will construct for its config file
# We need to mock this path when testing load_config
EXPECTED_CONFIG_PATH_IN_SCRAPER = os.path.join(PROJECT_ROOT_FOR_TESTS, "config", "config.yaml")

class TestScraper(unittest.TestCase):

    @patch('Job_Search.src.scraper.os.path.exists')  # Target 'os.path.exists' as used in scraper.py
    @patch('builtins.open', new_callable=mock_open)  # Mock open for file reading
    def test_load_config_success(self, mock_file_open, mock_path_exists):
        """Test successful loading of configuration."""
        mock_path_exists.return_value = True  # Simulate config file exists
        mock_config_data = {
            'scraping': {
                'job_boards': [{'url': 'http://example.com', 'query_params': {'q': 'test'}}]
            }
        }
        # Configure mock_open to return a file-like object that yaml.safe_load can use
        mock_file_open.return_value.read.return_value = yaml.dump(mock_config_data)
        
        config = load_config()
        
        mock_path_exists.assert_called_once_with(EXPECTED_CONFIG_PATH_IN_SCRAPER)
        mock_file_open.assert_called_once_with(EXPECTED_CONFIG_PATH_IN_SCRAPER, 'r')
        self.assertEqual(config, mock_config_data)

    @patch('Job_Search.src.scraper.os.path.exists')
    def test_load_config_file_not_found(self, mock_path_exists):
        """Test load_config when config file does not exist."""
        mock_path_exists.return_value = False  # Simulate config file does NOT exist
        # Expect load_config to print an error and return None
        with patch('builtins.print') as mock_print:
            config = load_config()
            self.assertIsNone(config)
            mock_print.assert_called_with(f"Error: Configuration file not found at {EXPECTED_CONFIG_PATH_IN_SCRAPER}")

    @patch('Job_Search.src.scraper.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_yaml_error(self, mock_file_open, mock_path_exists):
        """Test load_config with invalid YAML content."""
        mock_path_exists.return_value = True
        mock_file_open.return_value.read.return_value = "invalid: yaml: content: اینجا"
        
        with patch('builtins.print') as mock_print:
            config = load_config()
            self.assertIsNone(config)
            self.assertTrue(mock_print.call_args[0][0].startswith("Error parsing YAML configuration:"))

    @patch('Job_Search.src.scraper.requests.get')
    def test_scrape_job_board_success(self, mock_requests_get):
        """Test successful scraping of a single job board."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate HTML content - adjust class names to match scraper.py's expectations
        mock_response.text = """
        <html><body>
            <div class='job-card'>
                <h2>Software Engineer</h2>
                <span class='company'>TestCo</span>
                <a href='/job1'>Link</a>
                <span class='location'>Remote</span>
                <ul class='skills-list'><li>Python</li><li>Django</li></ul>
                <div class='description'>Looking for a Python developer...</div>
            </div>
            <div class='job-card'>
                <h2>Data Analyst</h2>
                <span class='company'>AnotherCo</span>
                <a href='http://example.com/job2'>Link</a>
                <span class='location'>New York, NY</span>
                <ul class='skills-list'><li>R</li><li>SQL</li></ul>
                <div class='description'>Seeking a data analyst...</div>
            </div>
        </body></html>
        """
        mock_response.raise_for_status = MagicMock()  # Mock this method
        mock_requests_get.return_value = mock_response
        
        jobs = scrape_job_board('http://example.com/jobs', {'q': 'dev'})
        
        mock_requests_get.assert_called_once_with('http://example.com/jobs', params={'q': 'dev'}, timeout=10)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['title'], 'Software Engineer')
        self.assertEqual(jobs[0]['company'], 'TestCo')
        self.assertEqual(jobs[0]['link'], 'http://example.com/job1')  # Relative URL resolved
        self.assertEqual(jobs[0]['location'], 'Remote')
        self.assertEqual(jobs[0]['skills'], ['Python', 'Django'])
        self.assertEqual(jobs[0]['description'], 'Looking for a Python developer...')
        self.assertEqual(jobs[1]['title'], 'Data Analyst')

    @patch('Job_Search.src.scraper.requests.get')
    def test_scrape_job_board_http_error(self, mock_requests_get):
        """Test scrape_job_board when an HTTP error occurs."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_requests_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            jobs = scrape_job_board('http://example.com/failing', {})
            self.assertEqual(jobs, [])
            self.assertTrue(mock_print.call_args[0][0].startswith("Failed to fetch data from http://example.com/failing:"))

    @patch('Job_Search.src.scraper.requests.get')
    def test_scrape_job_board_request_exception(self, mock_requests_get):
        """Test scrape_job_board with a general request exception."""
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch('builtins.print') as mock_print:
            jobs = scrape_job_board('http://example.com/failing', {})
            self.assertEqual(jobs, [])
            self.assertTrue(mock_print.call_args[0][0].startswith("Failed to fetch data from http://example.com/failing: Connection failed"))

    @patch('Job_Search.src.scraper.requests.get')
    def test_scrape_job_board_no_jobs_found(self, mock_requests_get):
        """Test scrape_job_board when response is OK but no job elements are found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>No jobs here</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            jobs = scrape_job_board('http://example.com/nojobs', {})
            self.assertEqual(jobs, [])
            # Check for the specific print message about no job elements found
            self.assertTrue(any("No job elements found on http://example.com/nojobs" in call[0][0] for call in mock_print.call_args_list))

    # Mock load_config for scrape_jobs tests
    @patch('Job_Search.src.scraper.load_config') 
    @patch('Job_Search.src.scraper.scrape_job_board')
    def test_scrape_jobs_success(self, mock_scrape_board, mock_load_cfg):
        """Test scrape_jobs successfully scrapes from multiple configured boards."""
        mock_load_cfg.return_value = {
            'scraping': {
                'job_boards': [
                    {'url': 'http://board1.com', 'query_params': {'q': 'eng'}},
                    {'url': 'http://board2.com', 'query_params': {'k': 'sci'}}
                ]
            }
        }
        # Define what scrape_job_board returns for each call
        mock_scrape_board.side_effect = [
            [{'title': 'Job1 from Board1', 'company': 'Company A', 'location': 'Remote'}],  # First call
            [{'title': 'Job2 from Board2', 'company': 'Company B', 'location': 'San Francisco, CA'}]  # Second call
        ]
        
        all_jobs = scrape_jobs()
        
        self.assertEqual(mock_scrape_board.call_count, 2)
        mock_scrape_board.assert_any_call('http://board1.com', {'q': 'eng'})
        mock_scrape_board.assert_any_call('http://board2.com', {'k': 'sci'})
        self.assertEqual(len(all_jobs), 2)
        self.assertIn({'title': 'Job1 from Board1', 'company': 'Company A', 'location': 'Remote'}, all_jobs)
        self.assertIn({'title': 'Job2 from Board2', 'company': 'Company B', 'location': 'San Francisco, CA'}, all_jobs)

    @patch('Job_Search.src.scraper.load_config')
    def test_scrape_jobs_config_load_fails(self, mock_load_cfg):
        """Test scrape_jobs when configuration loading fails."""
        mock_load_cfg.return_value = None  # Simulate config load failure
        with patch('builtins.print') as mock_print:
            all_jobs = scrape_jobs()
            self.assertEqual(all_jobs, [])
            self.assertTrue(any("Error: Scraping configuration is missing" in call[0][0] for call in mock_print.call_args_list))

    @patch('Job_Search.src.scraper.load_config')
    @patch('Job_Search.src.scraper.scrape_job_board')
    def test_scrape_jobs_board_url_missing(self, mock_scrape_board, mock_load_cfg):
        """Test scrape_jobs when a board URL is missing in config."""
        mock_load_cfg.return_value = {
            'scraping': {
                'job_boards': [
                    {'query_params': {'q': 'eng'}},  # Missing URL
                    {'url': 'http://board2.com', 'query_params': {'k': 'sci'}}
                ]
            }
        }
        mock_scrape_board.return_value = [{'title': 'Job from Board2', 'company': 'Company C', 'location': 'Austin, TX'}]
        
        with patch('builtins.print') as mock_print:
            all_jobs = scrape_jobs()
            self.assertEqual(len(all_jobs), 1)
            self.assertEqual(all_jobs[0]['title'], 'Job from Board2')
            mock_scrape_board.assert_called_once_with('http://board2.com', {'k': 'sci'})  # Only called for valid board
            self.assertTrue(any("Missing URL for a job board" in call[0][0] for call in mock_print.call_args_list))

if __name__ == '__main__':
    unittest.main()
