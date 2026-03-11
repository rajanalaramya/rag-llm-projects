import requests

def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response =requests.get(url).json()
    return response.get("abstractText", "No results found.")