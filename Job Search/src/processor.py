import logging
import re # For potential regex use in normalization
# from bs4 import BeautifulSoup # If HTML cleaning is needed for job descriptions

logger = logging.getLogger(__name__)

def normalize_text(text):
    """Basic text normalization: lowercase and remove extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with single
    return text

def create_job_fingerprint(job):
    """Creates a comparable fingerprint for a job to identify duplicates."""
    # A tuple of key fields, normalized, can serve as a fingerprint.
    # Ensure fields exist and are strings before normalizing.
    title = normalize_text(job.get('title', ''))
    company = normalize_text(job.get('company', ''))
    # Link might be too variable if it includes tracking params, but useful if canonical.
    # For now, focusing on title and company for deduplication.
    # Add more fields if necessary for uniqueness, e.g., location, or a snippet of description.
    return (title, company)

def clean_data(jobs):
    if not isinstance(jobs, list):
        logger.error("clean_data expects a list of job data.")
        return []

    cleaned_jobs = []
    seen_fingerprints = set()

    for job in jobs:
        if not isinstance(job, dict):
            logger.warning(f"Skipping non-dictionary item in jobs list: {job}")
            continue

        # 1. Basic Validation (ensure essential fields are somewhat present)
        #    Adjust required_fields as necessary for your data source.
        required_fields = ['title', 'company', 'link']
        if not all(job.get(field) for field in required_fields):
            logger.warning(f"Skipping job with missing essential fields: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            continue

        # 2. Normalization (example: job titles, company names)
        #    This is a placeholder. More sophisticated normalization might be needed.
        #    For example, you might want to normalize 'Software Engineer' and 'SW Eng.' to the same value.
        # job['title'] = normalize_text(job.get('title', ''))
        # job['company'] = normalize_text(job.get('company', ''))
        # Note: Modifying job dict directly. If the original is needed, copy first: job = job.copy()

        # 3. Deduplication (more efficient)
        fingerprint = create_job_fingerprint(job)
        if fingerprint not in seen_fingerprints:
            seen_fingerprints.add(fingerprint)
            cleaned_jobs.append(job)
        else:
            logger.info(f"Duplicate job found and removed: {job.get('title')} at {job.get('company')}")

    # 4. Filtering Irrelevant Jobs (Placeholder)
    #    Example: Filter out jobs with 'intern' in title if not desired.
    # final_jobs = [job for job in cleaned_jobs if 'intern' not in job.get('title', '').lower()]
    # For now, returning cleaned_jobs without this filter.
    final_jobs = cleaned_jobs

    logger.info(f"Original job count: {len(jobs)}, Cleaned job count: {len(final_jobs)}")
    return final_jobs
