from router import route_question
from memory import add_to_memory, get_memory
from calculator import calculator
from web_search import web_search
from rag_tool import rag_search
#from vector_store import VectorStore

while True:
    question = input("Ask a question (or type 'exit' to quit): ")
    if question.lower() == "exit":
        break
    tool = route_question(question)
    print("agent selected tool:",tool)
    if tool == "calculator":
        answer = calculator(question)
    elif tool == "web_search":
        answer = web_search(question)
    elif tool == "rag_search":
        answer = rag_search(question)
    elif tool == "memory":
        answer = get_memory()
    else:
        answer = "Sorry, I don't know how to handle that question."

    print("Answer:", answer.page_content)
    add_to_memory(question, answer)