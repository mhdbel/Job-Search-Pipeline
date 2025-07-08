import logging
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss  # For local vector database
# from pinecone import Pinecone  # Uncomment if using Pinecone

logger = logging.getLogger(__name__)

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def normalize_text(text):
    """Basic text normalization: lowercase and remove extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single
    return text

def create_job_fingerprint(job):
    """Creates a comparable fingerprint for a job to identify duplicates."""
    title = normalize_text(job.get('title', ''))
    company = normalize_text(job.get('company', ''))
    return (title, company)

def clean_data(jobs):
    """Cleans and deduplicates job data."""
    if not isinstance(jobs, list):
        logger.error("clean_data expects a list of job data.")
        return []

    cleaned_jobs = []
    seen_fingerprints = set()

    for job in jobs:
        if not isinstance(job, dict):
            logger.warning(f"Skipping non-dictionary item in jobs list: {job}")
            continue

        # Basic Validation
        required_fields = ['title', 'company', 'link']
        if not all(job.get(field) for field in required_fields):
            logger.warning(f"Skipping job with missing essential fields: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            continue

        # Deduplication
        fingerprint = create_job_fingerprint(job)
        if fingerprint not in seen_fingerprints:
            seen_fingerprints.add(fingerprint)
            cleaned_jobs.append(job)
        else:
            logger.info(f"Duplicate job found and removed: {job.get('title')} at {job.get('company')}")

    logger.info(f"Original job count: {len(jobs)}, Cleaned job count: {len(cleaned_jobs)}")
    return cleaned_jobs

def generate_embeddings(jobs):
    """Generates embeddings for job descriptions."""
    descriptions = [normalize_text(job.get('description', '')) for job in jobs]
    embeddings = embedding_model.encode(descriptions)
    return embeddings

def index_jobs_in_faiss(jobs):
    """Indexes jobs in a FAISS vector database."""
    embeddings = generate_embeddings(jobs)
    dimension = embeddings.shape[1]  # Dimensionality of embeddings
    index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search
    index.add(np.array(embeddings))

    # Store job metadata separately
    job_metadata = {i: job for i, job in enumerate(jobs)}
    logger.info(f"Indexed {len(jobs)} jobs into FAISS.")
    return index, job_metadata

# Example usage for Pinecone (optional)
# def index_jobs_in_pinecone(jobs, api_key, index_name):
#     pinecone.init(api_key=api_key, environment="us-west1-gcp")
#     if index_name not in pinecone.list_indexes():
#         pinecone.create_index(index_name, dimension=384)  # Adjust dimension based on model
#     index = pinecone.Index(index_name)
#
#     embeddings = generate_embeddings(jobs)
#     ids = [str(i) for i in range(len(jobs))]
#     metadata = [{key: job[key] for key in job} for job in jobs]
#     to_upsert = [(ids[i], embeddings[i].tolist(), metadata[i]) for i in range(len(jobs))]
#     index.upsert(to_upsert)
#     logger.info(f"Indexed {len(jobs)} jobs into Pinecone.")
#     return index

if __name__ == "__main__":
    # Example usage
    jobs = [
        {"title": "Python Developer", "company": "Company A", "description": "We are looking for a Python developer...", "link": "https://example.com/job/123 "},
        {"title": "Data Scientist", "company": "Company B", "description": "Seeking a data scientist with expertise in ML...", "link": "https://example.com/job/456 "}
    ]
    cleaned_jobs = clean_data(jobs)
    index, job_metadata = index_jobs_in_faiss(cleaned_jobs)

    # Test querying (example)
    query = "Find me remote Python developer jobs."
    query_embedding = embedding_model.encode(normalize_text(query))
    distances, indices = index.search(np.array([query_embedding]), k=2)
    print("Retrieved jobs:")
    for idx in indices[0]:
        print(job_metadata[idx])
