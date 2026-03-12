def route_question(question):
    question = question.lower()
    if any(char.isdigit() for char in question):
        return "calculator"
    elif "explain" in question or "what is" in question:
        return "rag_search"
    elif "news" in question or "latest" in question:
        return "web_search"
    elif "history" in question or "previous" in question:
        return "memory"
    else:
        return "rag_search"