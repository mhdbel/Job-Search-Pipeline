from scraper import scrape_jobs
from processor import clean_data
from analyzer import analyze_jobs
from notifier import notify
from logger import setup_logger

def main():
    logger = setup_logger()
    try:
        logger.info("Starting job scraping pipeline...")
        jobs = scrape_jobs()
        logger.info(f"Scraped {len(jobs)} jobs.")

        cleaned_jobs = clean_data(jobs)
        logger.info(f"Cleaned data contains {len(cleaned_jobs)} jobs.")

        interesting_jobs = analyze_jobs(cleaned_jobs)
        logger.info(f"Found {len(interesting_jobs)} interesting jobs.")

        config = load_config()
        notify(interesting_jobs, config)
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")

if __name__ == "__main__":
    main()