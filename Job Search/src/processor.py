def clean_data(jobs):
    cleaned_jobs = []
    for job in jobs:
        # Remove duplicates or irrelevant entries
        if job not in cleaned_jobs:
            cleaned_jobs.append(job)
    return cleaned_jobs