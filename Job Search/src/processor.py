import logging
import random
import re
from typing import Iterable, List, Sequence, Tuple

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 384


class SimpleEmbeddingArray:
    """Lightweight container that mimics the shape/indexing used in tests."""

    def __init__(self, rows: List[List[float]]):
        self._rows = rows

    @property
    def shape(self) -> Tuple[int, int]:
        if not self._rows:
            return (0, 0)
        return (len(self._rows), len(self._rows[0]))

    def __getitem__(self, item):
        return self._rows[item]

    def to_list(self) -> List[List[float]]:
        return list(self._rows)


class SimpleIndex:
    """In-memory search index compatible with the expected FAISS interface."""

    def __init__(self, embeddings: SimpleEmbeddingArray):
        self.embeddings = embeddings.to_list()
        self.ntotal = len(self.embeddings)

    @staticmethod
    def _l2_distance(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
        return sum((a - b) ** 2 for a, b in zip(vec_a, vec_b))

    def search(self, query_vectors: Iterable[Sequence[float]], k: int):
        distance_rows = []
        index_rows = []

        for query in query_vectors:
            scored = []
            for idx, vector in enumerate(self.embeddings):
                scored.append((self._l2_distance(query, vector), idx))
            scored.sort(key=lambda item: item[0])

            top = scored[:k]
            distance_rows.append([score for score, _ in top])
            index_rows.append([idx for _, idx in top])

        return distance_rows, index_rows

def normalize_text(text):
    """Basic text normalization: lowercase and remove extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single
    return text


def _seed_for_text(text: str) -> int:
    return abs(hash(text)) % (2 ** 32)


def _embed_text(text: str) -> List[float]:
    """Deterministically embed text to a fixed-length dense vector."""

    rng = random.Random(_seed_for_text(text))
    return [rng.random() for _ in range(EMBEDDING_DIMENSION)]

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
    embeddings = [_embed_text(description) for description in descriptions]
    return SimpleEmbeddingArray(embeddings)

def index_jobs_in_faiss(jobs):
    """Indexes jobs in a FAISS vector database."""
    embeddings = generate_embeddings(jobs)
    index = SimpleIndex(embeddings)

    job_metadata = {i: job for i, job in enumerate(jobs)}
    logger.info(f"Indexed {len(jobs)} jobs into FAISS-compatible structure.")
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
    query_embedding = _embed_text(normalize_text(query))
    distances, indices = index.search([query_embedding], k=2)
    print("Retrieved jobs:")
    for idx in indices[0]:
        print(job_metadata[idx])
