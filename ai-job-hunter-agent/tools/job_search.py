import requests

def job_search(query):
    """
    Searches for jobs based on the query.
    """
    # Placeholder for job search logic
    # In a real implementation, this would query a job database or API
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url)
    jobs = response.json().get("jobs")
    print("Total jobs fetched:", len(jobs))
    matches = []
    for job in jobs:
        title = job.get("title", "")
        if any(query.lower() in title.lower() for query in query.split()):
            matches.append({
                "title": title,
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "description": job.get("description"),
                "link": job.get("url"),
                "publication_date": job.get("publication_date")
            })
    return matches