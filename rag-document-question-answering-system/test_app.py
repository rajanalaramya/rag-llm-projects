import os
import dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

dotenv.load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("set GROQ API KEY")

client = Groq(api_key=api_key)

Loader =PyPDFLoader("C:/Users/maris/Downloads/rag_test_document.pdf")

splitter = RecursiveCharacterTextSplitter(chunk_size=800,chunk_overlap=100)
chunks = splitter.split_documents(Loader.load())
embeddings = HuggingFaceEmbeddings(model_name ="sentence-transformers/all-MiniLM-L6-v2")

vectorstore =Chroma.from_documents(
    documents = chunks,
    embedding = embeddings,
    persist_directory = "./vector_db",
    collection_name = "rag_collection",
    collection_metadata = {"hnsw:space":"cosine"}
)

while True:
    query = input("ask your question:")
    if query.lower()=='exit':
        break
    results = vectorstore.similarity_search(query,k=3)
    context = "\n\n".join([doc.page_content for doc in results])
    prompt = f"""
        answer the question using the below context. 
           context:context  
            question:{query} """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"You are a helpful RAG assistant that answers questions based on the provided context."},
                  {"role":"user","content":prompt}],
        max_tokens=500,
        temperature=0.2,
    )

    print("\nAnswer:\n",response.choices[0].message.content)



