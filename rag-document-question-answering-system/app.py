import os
import streamlit as st
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()

if "messages" not in st.session_state:
    st.session_state.messages=[]

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("set GROQ_API_KEY")
client = Groq(api_key=api_key)

st.set_page_config(page_title="RAG PDF Q&A", page_icon="📄",layout="wide")
st.title("📄 RAG PDF Q&A")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
if uploaded_file is not None:
    with st.spinner("Processing document..."):
    #save uploaded file to temporary location
        temp_path = f"./temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())  
        

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./vector_db",
            collection_name="rag_collection",
            collection_metadata={"hnsw:space": "cosine"}
        )
    st.success("Document processed! You can now ask questions about it.")
    #query = st.text_input("Ask a question about the document:")
    #Display chat messages and input
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    query = st.chat_input("Ask a question about the document:")
    if query:
        with st.spinner("Retrieving answer..."):
            st.session_state.messages.append({"role":"user","content":query})
            with st.chat_message("user"):
                st.markdown(query)

            #retrieve context from vectorstore
            results = vectorstore.similarity_search(query, k=3)
            context = "\n\n".join([doc.page_content for doc in results])
            prompt = f"""
                Answer the question using the below context.
                Context:
                {context}
                Question: {query}
                Answer:"""
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "You are a helpful RAG assistant that answers questions based on the provided context."},
                          {"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
            )
        st.subheader("Answer:")
        st.write(response.choices[0].message.content)
        # st.subheader("Retrieved Context:")
        # st.write(context)