import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.title("📄 PDF Chatbot (RAG)")

pdf = st.file_uploader("Upload your PDF", type="pdf")

if pdf is not None:
    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content

    with st.spinner("Processing PDF..."):
        splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_texts(chunks, embeddings)

    api_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key
    )

    query = st.text_input("Ask something about your PDF:")

    if query:
        docs = vectorstore.similarity_search(query, k=3)
        context = "\n".join([d.page_content for d in docs])

        messages = [
            SystemMessage(content=f"Answer based on this context:\n{context}"),
            HumanMessage(content=query)
        ]

        result = llm.invoke(messages)

        st.write("### Answer:")
        st.write(result.content)