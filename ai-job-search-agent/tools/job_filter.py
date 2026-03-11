import streamlit as st
import dotenv
import os
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import ast

dotenv.load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def filter_job(jobs, filters):
    """Filters the list of jobs based on the provided filters."""
    """jobs: List of job dicts
    filters: dictionary like "title": "python developer"
    """
    print("Filtering jobs with filters:", filters)
    today = datetime.today()
    filtered_jobs = []
    for job in jobs:
        keep = True
        if filters.get("keywords"):
            keyword_found = any(
                kw.lower() in (job.get("title","") + " " + job.get("description","")).lower()
                for kw in filters["keywords"]
            )
            if not keyword_found:
                keep = False
        if filters.get("location"):
            if filters["location"].lower() not in job.get("location","").lower():
                keep = False
        if filters.get("skills"):
            skill_found = any(
                skill.lower() in (job.get("title","") + " " + job.get("description","")).lower()
                for skill in filters["skills"]
            )
            if not skill_found:
                keep = False
        if filters.get("posted_within_days"):
            job_date_str = job.get("publication_date")
            if job_date_str:
                try:
                    job_date = datetime.fromisoformat(job_date_str)
                    days_diff = (today - job_date).days
                    if days_diff > filters["posted_within_days"]:
                        keep = False
                except:
                    # If date parsing fails, discard job
                    keep = False

        if keep:
            filtered_jobs.append(job)

    return filtered_jobs

def extract_filters_with_llm(query):
    """
    Given a user query, use LLM to extract structured filters.
    Returns a dict like:
    {
        "keywords": ["AI"],
        "location": "remote",
        "skills": ["python"],
        "posted_within_days": 5
    }
    """

    # ---- LLM Prompt ----
    prompt = f"""
    You are an AI system that extracts structured filters for job searches.

    Allowed filters:
    - keywords
    - location
    - skills
    - posted_within_days
    - experience_level
    - salary_min

    User query: "{query}"

    Return ONLY JSON with these fields.
    If a field is not specified, return null or empty list.
    Example:
    {{
      "keywords": ["AI"],
      "location": "remote",
      "skills": ["python"],
      "posted_within_days": 5,
      "experience_level": null,
      "salary_min": null
    }}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "you are an assistant that helps users find jobs. You have access to the following tools: 1. job_search(query): Searches for jobs based on the query. 2. filter_job(jobs, filters): Filters the list of jobs based on the provided filters. 3. summarize_job(job): Summarizes the job details into a concise format. Given the user's query, decide which tool(s) to use to best answer the query. Your response should be a list of tool names in the order they should be executed."},
                  {"role": "user", "content": prompt}]
    )
    llm_output = response.choices[0].message.content
    match = re.search(r"\{.*\}", llm_output, re.DOTALL)
    if match:
        raw_text = match.group()
        try:
            # First try parsing as JSON
            filters = json.loads(raw_text)
        except:
            # If JSON fails, try Python literal eval
            try:
                filters = ast.literal_eval(raw_text)
            except:
                filters = {
                    "keywords": [],
                    "location": None,
                    "skills": [],
                    "posted_within_days": None,
                    "experience_level": None,
                    "salary_min": None
                }
    else:
        filters = {
            "keywords": [],
            "location": None,
            "skills": [],
            "posted_within_days": None,
            "experience_level": None,
            "salary_min": None
        }

    return filters
