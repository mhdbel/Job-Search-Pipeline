import requests
from bs4 import BeautifulSoup
import yaml
import os

# Determine the absolute path to the project root directory
# Assuming this script is in Job Search/src/
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT is the directory containing 'src', 'config', etc.
# If scraper.py is in Job Search/src/, then SRC_DIR is Job Search/src/
# and PROJECT_ROOT should be Job Search/
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_FILE_PATH = os.path.join(PROJECT_ROOT, "config", "config.yaml")

def load_config():
    if not os.path.exists(CONFIG_FILE_PATH):
        # Handle the case where the config file doesn't exist
        print(f"Error: Configuration file not found at {CONFIG_FILE_PATH}")
        return None # Or raise an exception
    with open(CONFIG_FILE_PATH, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            return None # Or raise an exception

def scrape_job_board(url, params):
    try:
        response = requests.get(url, params=params, timeout=10) # Added timeout
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    # The following selectors are placeholders and need to be adjusted based on actual job board HTML
    # It's crucial that these selectors match the structure of the websites you're scraping.
    job_elements = soup.find_all("div", class_="job-card") # Example selector, adjust as needed
    if not job_elements:
        print(f"No job elements found on {url} with the selector 'div.job-card'. This might indicate a change in website structure or an incorrect selector.")

    for job_element in job_elements:
        title_element = job_element.find("h2") # Example selector
        company_element = job_element.find("span", class_="company") # Example selector
        link_element = job_element.find("a", href=True) # Ensure 'a' tag has href

        title = title_element.text.strip() if title_element else "N/A"
        company = company_element.text.strip() if company_element else "N/A"
        # Ensure link is absolute or correctly formed if relative
        link = link_element["href"] if link_element else "#"
        if link_element and not link.startswith('http'):
            # This is a simplistic way to handle relative URLs, might need base URL joining
            # from urllib.parse import urljoin
            # link = urljoin(url, link)
            pass # Placeholder for proper relative URL handling
            
        jobs.append({"title": title, "company": company, "link": link})
    return jobs

def scrape_jobs():
    config = load_config()
    all_jobs = []
    if not config or 'scraping' not in config or not isinstance(config.get('scraping', {}).get('job_boards'), list):
        print("Error: Scraping configuration is missing, malformed, or 'job_boards' is not a list.")
        return []
        
    for board in config["scraping"]["job_boards"]:
        url = board.get("url")
        params = board.get("query_params")
        if not url:
            print(f"Warning: Missing URL for a job board in config. Skipping entry: {board}")
            continue
        print(f"Scraping {url} with params: {params}") # Added for verbosity
        jobs_from_board = scrape_job_board(url, params if params else {})
        if jobs_from_board:
            print(f"Found {len(jobs_from_board)} jobs from {url}")
            all_jobs.extend(jobs_from_board)
        else:
            print(f"No jobs found or error scraping {url}")
    return all_jobs
