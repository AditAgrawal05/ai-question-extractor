# core/pipeline.py

import os
import json
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT
from tqdm import tqdm # Import the progress bar library

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file")

def create_rag_pipeline(pdf_path: str):
    """
    Initializes and returns a RAG pipeline for question extraction using Gemini.
    """
    print("Setting up RAG pipeline with Gemini models...")
    
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from the book.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    print(f"Split document into {len(split_docs)} chunks.")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # --- START OF THE FIX: ADDING A PROGRESS BAR ---
    print("Creating vector store. This is the slow step due to API rate limits...")
    
    # Initialize the vector store with the first document
    vector_store = FAISS.from_documents([split_docs[0]], embeddings)
    
    # Add the rest of the documents with a progress bar
    # This will show you the progress chunk by chunk.
    for doc in tqdm(split_docs[1:], desc="Embedding Chunks"):
        vector_store.add_documents([doc])
        
    print("Vector store created successfully.")
    # --- END OF THE FIX ---

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    prompt_template = (
        SYSTEM_PROMPT
        + """

    Based on the context provided below, please extract the questions.

    CONTEXT:
    {context}

    USER'S REQUEST:
    {input}
    """
    )
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 15})
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    print("Gemini RAG pipeline is ready.")
    return retrieval_chain


def extract_questions(pipeline, chapter_number: int, topic_name: str) -> list[str]:
    """
    Runs the RAG pipeline to extract questions for a given chapter and topic.
    """
    query = f"Extract all practice questions and question-like illustrations from Chapter {chapter_number} about '{topic_name}' from the RD Sharma book."
    
    print(f"\nExecuting query: {query}")
    response = pipeline.invoke({"input": query})
    
    answer_str = response.get("answer", "")
    
    try:
        clean_json_str = answer_str.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json_str)
        extracted_list = data.get("answer", [])

        if isinstance(extracted_list, list):
            return extracted_list
        else:
            return []

    except (json.JSONDecodeError, AttributeError):
        print("Warning: Could not parse the AI's response as JSON. The output may be incomplete.")
        return [line.strip() for line in answer_str.split('\n') if line.strip()]