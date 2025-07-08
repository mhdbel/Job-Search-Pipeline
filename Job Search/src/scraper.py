import requests
from bs4 import BeautifulSoup
import yaml
import os
import json
from urllib.parse import urljoin

# Determine the absolute path to the project root directory
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_FILE_PATH = os.path.join(PROJECT_ROOT, "config", "config.yaml")

def load_config():
    """Load configuration from the YAML file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Error: Configuration file not found at {CONFIG_FILE_PATH}")
        return None
    try:
        with open(CONFIG_FILE_PATH, "r") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return None

def save_jobs_to_file(jobs, output_file):
    """Save scraped jobs to a JSON file."""
    try:
        with open(output_file, "w") as file:
            json.dump(jobs, file, indent=4)
        print(f"Saved {len(jobs)} jobs to {output_file}")
    except Exception as e:
        print(f"Error saving jobs to {output_file}: {e}")

def scrape_job_board(url, params):
    """Scrape job postings from a single job board."""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    # Example selectors (adjust based on the actual HTML structure of the job board)
    job_elements = soup.find_all("div", class_="job-card")
    if not job_elements:
        print(f"No job elements found on {url} with the selector 'div.job-card'.")
        return []

    for job_element in job_elements:
        # Extract title
        title_element = job_element.find("h2")
        title = title_element.text.strip() if title_element else "N/A"

        # Extract company
        company_element = job_element.find("span", class_="company")
        company = company_element.text.strip() if company_element else "N/A"

        # Extract location
        location_element = job_element.find("span", class_="location")
        location = location_element.text.strip() if location_element else "N/A"

        # Extract description
        description_element = job_element.find("div", class_="description")
        description = description_element.text.strip() if description_element else "N/A"

        # Extract skills (if available)
        skills_element = job_element.find("ul", class_="skills-list")
        skills = [skill.text.strip() for skill in skills_element.find_all("li")] if skills_element else []

        # Extract link
        link_element = job_element.find("a", href=True)
        link = link_element["href"] if link_element else "#"
        if link_element and not link.startswith('http'):
            # Handle relative URLs
            link = urljoin(url, link)

        # Append job details
        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "skills": skills,
            "link": link
        })

    return jobs

def scrape_jobs():
    """Scrape jobs from all configured job boards and save them to a file."""
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
        print(f"Scraping {url} with params: {params}")  # Added for verbosity
        jobs_from_board = scrape_job_board(url, params if params else {})
        if jobs_from_board:
            print(f"Found {len(jobs_from_board)} jobs from {url}")
            all_jobs.extend(jobs_from_board)
        else:
            print(f"No jobs found or error scraping {url}")

    # Save all scraped jobs to a JSON file
    output_file = os.path.join(PROJECT_ROOT, "output", "scraped_jobs.json")
    save_jobs_to_file(all_jobs, output_file)
    return all_jobs

if __name__ == "__main__":
    # Run the scraper when the script is executed directly
    scrape_jobs()
