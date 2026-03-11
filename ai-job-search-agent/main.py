import streamlit as st
from tools.job_search import job_search
from tools.job_summary import summarize_job
from tools.job_filter import filter_job
from agent_router import decide_tool
from agent_router import plan_tools
from agent_router import LLM_decide_tool
from tools.job_filter import extract_filters_with_llm


if "messages" not in st.session_state:
        st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
tools_map ={
    "job_search": job_search,
    "filter_job": filter_job,
    "summarize_job": summarize_job
}

def main():
    st.title("AI Job finder Agent")
    query = st.chat_input("Enter your job preferences", key="job_preferences")
    if query:
        st.session_state.messages.append({"role":"user","content":query})
        with st.chat_message("user"):
            st.write(query)

            #tool = decide_tool(query)
            # rule based tool decision
            #plan = plan_tools(query)

            #LLM based tool decision
            plan = LLM_decide_tool(query)
            jobs = None
            print("Selected tool:", plan)
            tools = [tools_map[t] for t in plan]
            print("-----------------------")
            for tool_name in tools:
                tool = tools_map[tool_name.__name__]
                print("Executing tool:", tool_name.__name__)
                if tool_name.__name__ == "summarize_job":
                    jobs = st.session_state.get("jobs", [])
                    with st.chat_message("assistant"):
                        st.write("Summarizing the first job in the list...")
                        if not jobs:
                            st.write("No jobs available to summarize.")
                            st.session_state.messages.append({"role":"assistant","content":"No jobs available to summarize."})
                            continue
                        summary = tool(jobs[0])
                        st.markdown(summary, unsafe_allow_html=True)
                        st.session_state.messages.append({"role":"assistant","content":summary})
                        st.write(summary)
                elif tool_name.__name__ == "filter_job":
                    jobs = st.session_state.get("jobs", [])
                     # Example filter based on query
                    with st.chat_message("assistant"):
                        st.write("Filtering jobs based on your query...")
                        filters = extract_filters_with_llm(query)
                        filtered_jobs = tool(jobs, filters)
                        print("Filtered jobs:", len(filtered_jobs))
                        st.session_state.jobs = filtered_jobs
                        st.session_state.messages.append({"role":"assistant","content":"Filtered jobs based on your query."})
                        st.write("Filtered {0} jobs based on your query.".format(len(filtered_jobs)))
                        display_jobs(filtered_jobs)
                elif tool_name.__name__ == "job_search":
                    jobs = tool(query)
                    print("Jobs found:", len(jobs))
                    st.session_state.jobs = jobs
                    with st.chat_message("assistant"):
                        st.write("Here’s what I found for your query: {} jobs.".format(len(jobs)))
                        st.session_state.messages.append({"role":"assistant","content":"Found {} jobs matching your query.".format(len(jobs))})
                        #display_jobs(jobs)
            # if tool == summarize_job:
            #     summary = tool()
            #     st.session_state.messages.append({"role":"assistant","content":summary})
            #     st.write(summary)
            #     return []
            # elif tool == filter_job:
            #     jobs = st.session_state.get("jobs", [])
            #     filters = {"title": query}  # Example filter based on query
            #     filtered_jobs = tool(jobs, filters)
            #     st.session_state.messages.append({"role":"assistant","content":"Filtered jobs based on your query."})
            #     st.write("Filtered jobs based on your query.")
            #     return filtered_jobs
            # else:
            #     jobs = tool(query)
            #     st.session_state.jobs = jobs
        # with st.chat_message("assistant"):
        #     if jobs is not None:

        #         st.write("Here’s what I found for your query:", len(jobs), "jobs.")
        #         display_jobs(jobs)
            
        #         st.session_state.messages.append({"role":"assistant","content":"Found {} jobs matching your query.".format(len(jobs))})
        #     else:
        #         st.write("Sorry, I couldn't find any jobs matching your query.")
        #         st.session_state.messages.append({"role":"assistant","content":"Sorry, I couldn't find any jobs matching your query."})
        # return jobs
    return []
    

def display_jobs(jobs):
    st.subheader("Job Listings")
    for job in jobs:
        st.write(f"**{job['title']}** at {job['company']}")
        st.write(f"Location: {job['location']}")
        st.markdown(job['description'], unsafe_allow_html=True)
        st.write(f"link: {job['link']}")
        st.write("---")
    #jobs = job_search.job_search(query)
    
if __name__ == "__main__":
    jobs = main()
    #print("Jobs found:", jobs)
    #display_jobs(jobs)

    