import streamlit as st


def summarize_job(job):
    """Summarizes the job details into a concise format."""
    
    if not job:
        return "No job to summarize."
    summary = f"**{job['title']}** at {job['company']}\n"
    summary += f"Location: {job['location']}\n"
    summary += f"Description: {job['description']}\n"
    summary += f"Link: {job['link']}\n"
    return summary
