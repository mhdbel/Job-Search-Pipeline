import logging
from rank_bm25 import BM25Okapi
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load embedding model for vector search
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def analyze_jobs(jobs):
    """Placeholder logic: Assume jobs with fewer than 10 applicants are 'interesting'."""
    interesting_jobs = []
    if not isinstance(jobs, list):
        logger.error("analyze_jobs expects a list of jobs.")
        return interesting_jobs  # Return empty list or raise error

    for job in jobs:
        if not isinstance(job, dict):
            logger.warning(f"Skipping non-dictionary job item: {job}")
            continue

        applicants_raw = job.get("applicants")
        applicants = 0  # Default value

        if applicants_raw is not None:
            if isinstance(applicants_raw, int):
                applicants = applicants_raw
            else:
                logger.warning(
                    f"Job ID '{job.get('id', 'N/A')}' has non-integer applicants value '{applicants_raw}'. Using default 0."
                )

        # Current logic: jobs with fewer than 10 applicants are "interesting"
        if applicants < 10:
            interesting_jobs.append(job)

    return interesting_jobs

def hybrid_search(query, jobs, index, top_k=5):
    """
    Perform hybrid search (keyword + vector search) to retrieve relevant jobs.
    
    Args:
        query (str): User query.
        jobs (list): List of job dictionaries.
        index (FAISS index): Vector database index.
        top_k (int): Number of results to return.
    
    Returns:
        list: Top-k most relevant jobs.
    """
    # Step 1: Keyword Filtering (BM25)
    tokenized_descriptions = [job["description"].split() for job in jobs]
    bm25 = BM25Okapi(tokenized_descriptions)
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    keyword_indices = np.argsort(scores)[::-1][:top_k]

    # Step 2: Vector Search (FAISS)
    query_embedding = embedding_model.encode(query)
    distances, vector_indices = index.search(np.array([query_embedding]), top_k)

    # Step 3: Combine Results
    combined_indices = set(keyword_indices).union(vector_indices[0])
    relevant_jobs = [jobs[i] for i in combined_indices if i < len(jobs)]  # Ensure indices are valid

    logger.info(f"Hybrid search retrieved {len(relevant_jobs)} jobs.")
    return relevant_jobs

if __name__ == "__main__":
    # Example usage
    jobs = [
        {"title": "Python Developer", "company": "Company A", "description": "We are looking for a Python developer...", "link": "https://example.com/job/123 "},
        {"title": "Data Scientist", "company": "Company B", "description": "Seeking a data scientist with expertise in ML...", "link": "https://example.com/job/456 "}
    ]

    # Generate embeddings and create FAISS index
    from processor import generate_embeddings, index_jobs_in_faiss
    embeddings = generate_embeddings(jobs)
    dimension = embeddings.shape[1]
    index = index_jobs_in_faiss(jobs)

    # Perform hybrid search
    query = "Find me remote Python developer jobs."
    relevant_jobs = hybrid_search(query, jobs, index, top_k=2)

    print("Retrieved jobs:")
    for job in relevant_jobs:
        print(job)
