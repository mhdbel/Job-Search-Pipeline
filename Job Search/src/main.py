from scraper import scrape_jobs, load_config  # MODIFIED LINE
from processor import clean_data, index_jobs_in_faiss
from analyzer import hybrid_search
from notifier import notify
from logger import setup_logger
from langchain.llms import OpenAI  # For generating responses using an LLM

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

        # Step 3: Index jobs in FAISS
        index, job_metadata = index_jobs_in_faiss(cleaned_jobs)
        logger.info(f"Indexed {len(cleaned_jobs)} jobs in FAISS.")

        # Step 4: Retrieve relevant jobs using hybrid search
        query = "Find me remote Python developer jobs."  # Example user query
        relevant_jobs = hybrid_search(query, cleaned_jobs, index, top_k=5)
        logger.info(f"Hybrid search retrieved {len(relevant_jobs)} relevant jobs.")

        # Step 5: Augment prompt
        context = "\n".join([f"{job['title']}: {job['description']} ({job['link']})" for job in relevant_jobs])
        augmented_prompt = f"Using the information below, answer the question.\n\n{context}\n\nQ: {query}"

        # Step 6: Generate response using an LLM
        llm = OpenAI(api_key=config["openai_api_key"])  # Replace with your OpenAI API key
        response = llm(augmented_prompt)
        logger.info(f"Generated response: {response}")

        # Step 7: Notify user (optional)
        notify(response, config)  # Pass the generated response to the notifier
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)  # Added exc_info for better debugging

if __name__ == "__main__":
    main()

