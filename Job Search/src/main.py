import os
from typing import List

from src.config import load_config
from src.scraper import scrape_jobs
from src.processor import clean_data, index_jobs_in_faiss
from src.analyzer import hybrid_search
from src.notifier import notify
from src.logger import setup_logger


def _build_response(query: str, jobs: List[dict]) -> str:
    """Create a simple text response summarizing the retrieved jobs."""

    if not jobs:
        return f"No results found for query: {query}"

    lines = [f"Query: {query}", "", "Top results:"]
    for job in jobs:
        lines.append(
            f"- {job.get('title', 'N/A')} at {job.get('company', 'N/A')}: {job.get('description', 'No description')}"
        )
    return "\n".join(lines)


def main():
    logger = setup_logger()
    try:
        logger.info("Starting job scraping pipeline...")

        # Load configuration first
        config = load_config()
        if config is None:
            logger.error("Failed to load configuration. Exiting pipeline.")
            return

        # Step 1: Scrape jobs
        jobs = scrape_jobs()  # scrape_jobs now uses the config loaded within it if needed
        logger.info(f"Scraped {len(jobs)} jobs.")

        # Step 2: Clean data
        cleaned_jobs = clean_data(jobs)
        logger.info(f"Cleaned data contains {len(cleaned_jobs)} jobs.")

        # Step 3: Index jobs
        index, job_metadata = index_jobs_in_faiss(cleaned_jobs)
        logger.info(f"Indexed {len(cleaned_jobs)} jobs in SimpleIndex store.")

        # Step 4: Retrieve relevant jobs using hybrid search
        query = "Find me remote Python developer jobs."  # Example user query
        relevant_jobs = hybrid_search(query, cleaned_jobs, index, top_k=5)
        logger.info(f"Hybrid search retrieved {len(relevant_jobs)} relevant jobs.")

        # Step 5: Generate a human-readable response
        response = _build_response(query, relevant_jobs)
        logger.info(f"Generated response: {response}")

        # Step 6: Notify user (optional)
        notify(response, config)  # Pass the generated response to the notifier
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)  # Added exc_info for better debugging


if __name__ == "__main__":
    main()
