from tools.job_search import job_search
from tools.job_summary import summarize_job
from tools.job_filter import filter_job
from groq import Groq
from dotenv import load_dotenv
import os 
import json 
import re, ast


def decide_tool(query):

    if any(word in query for word in ["search","jobs", "find", "search","ai"]):
        return job_search
    elif any(word in query for word in ["filter", "refine", "narrow"]):
        return filter_job
    elif any(word in query for word in ["summarize", "describe"]):
        return summarize_job
    

def plan_tools(query):
    """ Input: user query(string)
        output :List of tools to use in order to answer the query"""
    query_lower =query.lower()
    plan = []
    if any(word in query for word in ["search","ai","jobs","find","java"]):
        plan.append(job_search)
    if any(word in query for word in ["filter", "refine", "narrow","remote","senior"]):
        plan.append(filter_job) 
    if any(word in query for word in ["summarize", "describe","explain"]):
        plan.append(summarize_job)

    if job_search not in plan:
        plan.insert(0, job_search)
    return plan


def LLM_decide_tool(query):
    """Use LLM to decide which tool to use based on the query."""

    prompt = f"""
    You are an AI agent tool planner. You have access to the following tools:
    1. job_search(query): Searches for jobs based on the query.
    2. filter_job(jobs, filters): Filters the list of jobs based on the provided filters.
    3. summarize_job(job): Summarizes the job details into a concise format.
    User query: {query}
    Return ONLY valid JSON in this format:
    {{"tools": ["tool_name"]}}
    rules:
    -use only these tools: job_search, filter_job, summarize_job
    -donot explain anything.
    -output must be tools JSON.
    Correct output example:
        {{"tools":["job_search","filter_job"]}}

        Incorrect outputs:
        ❌ explanations
        ❌ numbered lists
        ❌ tool arguments
        ❌ sentences
    
    """
    load_dotenv()
    api_key  =os.getenv("GROQ_API_KEY")
    client = Groq(api_key = api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "you are an assistant that helps users find jobs. You have access to the following tools: 1. job_search(query): Searches for jobs based on the query. 2. filter_job(jobs, filters): Filters the list of jobs based on the provided filters. 3. summarize_job(job): Summarizes the job details into a concise format. Given the user's query, decide which tool(s) to use to best answer the query. Your response should be a list of tool names in the order they should be executed."},
                  {"role": "user", "content": prompt}]
    )

    llm_output = response.choices[0].message.content
    llm_data = json.loads(llm_output)

    match = re.search(r"\{.*\}", llm_output, re.DOTALL)
    if match:
        raw_json = match.group()
        try:
            llm_data = json.loads(raw_json)
        except:
            try:
                llm_data = ast.literal_eval(raw_json)
            except:
                llm_data = {"tools": []}
    else:
        llm_data = {"tools": []}

    tools_list = llm_data.get("tools", [])
    return tools_list


    # Placeholder for LLM logic
    # In a real implementation, this would use an LLM to analyze the query and decide which tool(s) to use
    