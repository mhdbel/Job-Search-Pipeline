import requests
from bs4 import BeautifulSoup
import yaml

def load_config():
    with open("../config/config.yaml", "r") as file:
        return yaml.safe_load(file)

def scrape_job_board(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        for job in soup.find_all("div", class_="job-card"):  # Adjust selector as needed
            title = job.find("h2").text.strip()
            company = job.find("span", class_="company").text.strip()
            link = job.find("a")["href"]
            jobs.append({"title": title, "company": company, "link": link})
        return jobs
    else:
        print(f"Failed to fetch data from {url}")
        return []

def scrape_jobs():
    config = load_config()
    all_jobs = []
    for board in config["scraping"]["job_boards"]:
        jobs = scrape_job_board(board["url"], board["query_params"])
        all_jobs.extend(jobs)
    return all_jobs