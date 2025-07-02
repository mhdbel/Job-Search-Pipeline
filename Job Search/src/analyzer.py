import logging # Added import for logging

# It's good practice to get a logger instance per module
logger = logging.getLogger(__name__)

def analyze_jobs(jobs):
    # Placeholder logic: Assume jobs with fewer than 10 applicants are "interesting"
    interesting_jobs = []
    if not isinstance(jobs, list):
        logger.error("analyze_jobs expects a list of jobs.")
        return interesting_jobs # Return empty list or raise error

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
                # Optionally, try to convert, e.g., if '5' (str) is common:
                # try:
                #     applicants = int(applicants_raw)
                # except ValueError:
                #     logger.warning(f"Could not convert applicants_raw '{applicants_raw}' to int.")
        
        # Current logic: jobs with fewer than 10 applicants are "interesting"
        # This assumes 'applicants' is a comparable number after the above block.
        if applicants < 10:
            interesting_jobs.append(job)
            
    return interesting_jobs
