from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

path = "./data/data.txt"
loader = TextLoader(path)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size =200, chunk_overlap=10)
docs= text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore =Chroma.from_documents(
    documents = docs,
    embedding = embeddings,
    collection_name = "my_collection")


def rag_search(query):
    results =vectorstore.similarity_search(query, k=3)
    return results
