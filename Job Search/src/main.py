from scraper import scrape_jobs, load_config # MODIFIED LINE
from processor import clean_data
from analyzer import analyze_jobs
from notifier import notify
from logger import setup_logger

def main():
    logger = setup_logger()
    try:
        logger.info("Starting job scraping pipeline...")
        
        # Load configuration first
        config = load_config()
        if config is None:
            logger.error("Failed to load configuration. Exiting pipeline.")
            return

        jobs = scrape_jobs() # scrape_jobs now uses the config loaded within it if needed
        logger.info(f"Scraped {len(jobs)} jobs.")

        cleaned_jobs = clean_data(jobs)
        logger.info(f"Cleaned data contains {len(cleaned_jobs)} jobs.")

        interesting_jobs = analyze_jobs(cleaned_jobs)
        logger.info(f"Found {len(interesting_jobs)} interesting jobs.")

        notify(interesting_jobs, config) # Pass the loaded config to notify
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True) # Added exc_info for better debugging

if __name__ == "__main__":
    main()

