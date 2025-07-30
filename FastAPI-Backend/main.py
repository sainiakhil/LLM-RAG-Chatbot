import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate 


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Fetch API keys from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not PINECONE_API_KEY or not GOOGLE_API_KEY:
    raise ValueError("API keys for Pinecone and OpenAI must be set in the .env file.")

# Configuration constants
PINECONE_INDEX_NAME = "changi-airport-knowledge-base"
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
LLM_MODEL_NAME = "gemini-1.5-flash-latest"


# --- NEW: Define a custom prompt template ---
prompt_template_str = """
You are a helpful and polite assistant for the Singapore Changi Airport.
Your task is to answer user questions accurately based ONLY on the context provided.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
1.  Read the CONTEXT carefully.
2.  Formulate your answer based solely on the information within the CONTEXT.
3.  If the answer is not found in the CONTEXT, you must politely state, "I'm sorry, I don't have information on that topic based on the provided website content."
4.  Do not use any external knowledge or make up information.
5.  Answer in a clear and concise manner.

ANSWER:
"""

# Create a PromptTemplate object
CUSTOM_PROMPT = PromptTemplate(
    template=prompt_template_str, input_variables=["context", "question"]
)


# --- 2. RAG Chain Initialization ---

def initialize_rag_chain():
    """Initializes and returns a RetrievalQA chain."""
    try:
        logging.info("Initializing RAG chain...")

        embeddings_wrapper = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        logging.info("Embeddings model wrapper initialized.")

        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings_wrapper
            
        )
        logging.info("Pinecone vector store initialized.")

        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            google_api_key = GOOGLE_API_KEY,
            max_output_tokens=2048,
            temperature=0.1 
        )
        logging.info("LLM initialized.")

    
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
            return_source_documents=False,
            chain_type_kwargs={"prompt": CUSTOM_PROMPT}

        )
        logging.info("RetrievalQA chain created successfully with custom prompt.")
        return qa_chain

    except Exception as e:
        logging.critical(f"Failed to initialize RAG chain: {e}", exc_info=True)
        raise RuntimeError("Could not initialize the RAG chain.") from e

# Initialize the chain and store it in a global variable
rag_chain = initialize_rag_chain()

# --- 4. FastAPI Application ---

app = FastAPI(
    title="Changi Airport Chatbot API",
    description="An API to answer questions about Changi Airport using a RAG model.",
    version="1.0.0"
)

# Pydantic models for data validation
class QueryRequest(BaseModel):
    question: str

# --- MODIFICATION: Simplified the response model ---
class QueryResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    logging.info(f"Received query: '{request.question}'")
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        # The result will no longer contain 'source_documents'
        result = rag_chain.invoke({"query": request.question})
        
        return QueryResponse(
            answer=result.get('result', 'No answer could be generated.')
        )
    except Exception as e:
        logging.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during query processing.")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Changi Airport Chatbot API is running. Append /docs to the URL to see the API documentation."}