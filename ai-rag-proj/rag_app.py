import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader 
from langchain_community.vectorstores import Chroma 
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()

#config
PDF_PATH = "C:/Users/maris/Downloads/rag_test_document.pdf"
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("set GROQ_API_KEY")

client = Groq(api_key=api_key)
#client = groq.Client(api_key=api_key)

# models = client.models.list()
# for m in models:
#     print(m.name, m.model_config)

#load PDF File
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

#split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 900,
    chunk_overlap = 100
)

chunks = splitter.split_documents(docs)

# print("\n List of Chunks:\n")
# for i,chunk in enumerate(chunks):
#     print(f"Chunk {i + 1} length: {len(chunk.page_content)}")
#     print("-----")

#print("chunks:",chunks)

#create embeddings and vector db

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./vector_db",
    collection_name="rag_collection",
    collection_metadata={"hnsw:space": "cosine"}
)
print("RAG system is ready")

#Queryloop
while True:
    query = input("ask about your document: ")
    if query.lower() == 'exit':
        break

    #retrieve similar chunks

    results = vectorstore.similarity_search(query,k=3)

    # print("\n--- Retrieved Chunks ---")
    # for doc in results:
    #     print(doc.page_content[:300])
    #     print("-----")

    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""
                answer the question using the below context.
                context:
                {context}
                question:
                {query}
            """
    # response = client.models.generate_content(
    #     model = "models/llama-3.1-8b-instant",
    #     contents = [prompt]
    # )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "you are helpful assistant that answers using provided context"},
            {"role":"user","content":prompt}
        ]
    )

    print("\n🤖 AI Answer:\n")
    #print(response.text)
    print(response.choices[0].message.content)



