import logging
from typing import List

from src.processor import normalize_text, _embed_text

logger = logging.getLogger(__name__)

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

        if isinstance(applicants_raw, int):
            applicants = applicants_raw
        else:
            if applicants_raw is not None:
                logger.warning(
                    f"Job ID '{job.get('id', 'N/A')}' has non-integer applicants value '{applicants_raw}'. Using default 0."
                )
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
    if not isinstance(query, str) or not query.strip():
        logger.warning("hybrid_search received an empty or non-string query; returning no results.")
        return []

    if not jobs or index is None:
        logger.warning("hybrid_search has no jobs or index to search against; returning no results.")
        return []

    normalized_query = normalize_text(query)

    # Step 1: Keyword Filtering (simple overlap score)
    tokenized_descriptions: List[List[str]] = []
    for job in jobs:
        description = normalize_text(job.get("description", ""))
        tokenized_descriptions.append(description.split())

    query_tokens = normalized_query.split()
    keyword_scores = []
    for tokens in tokenized_descriptions:
        overlap = sum(1 for token in tokens if token in query_tokens)
        keyword_scores.append(overlap)

    keyword_indices = sorted(range(len(keyword_scores)), key=lambda i: keyword_scores[i], reverse=True)[:top_k]

    # Step 2: Vector Search (SimpleIndex)
    query_embedding = _embed_text(normalized_query)
    distances, vector_indices = index.search([query_embedding], top_k)

    # Step 3: Combine Results
    combined_indices = set(int(idx) for idx in keyword_indices).union(int(i) for i in vector_indices[0])
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
    from src.processor import index_jobs_in_faiss

    index, metadata = index_jobs_in_faiss(jobs)

    # Perform hybrid search
    query = "Find me remote Python developer jobs."
    relevant_jobs = hybrid_search(query, jobs, index, top_k=2)

    print("Retrieved jobs:")
    for job in relevant_jobs:
        print(job)
