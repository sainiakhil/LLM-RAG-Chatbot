import logging
import os
import time
import uuid
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv  # <-- IMPORT THIS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm

# --- 1. Load Environment Variables ---
# This line loads the variables from your .env file
load_dotenv() 

# --- 2. Configuration ---
# Get credentials from the environment. Add a check to ensure they exist.
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env file. Please add it.")

PINECONE_INDEX_NAME = "changi-airport-knowledge-base"
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768
SITEMAP_URL = "https://www.changiairport.com/sitemap.xml"
BATCH_SIZE = 100
URL_PROCESS_LIMIT = 50 # Set to None to process all URLs

# --- 3. Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ... (The rest of your helper functions: get_urls_from_sitemap, scrape_and_clean_page, etc. remain exactly the same) ...

def get_urls_from_sitemap(session: requests.Session, sitemap_url: str) -> List[str]:
    # (This function does not need any changes)
    logging.info(f"Fetching sitemap from: {sitemap_url}")
    try:
        response = session.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml-xml')
        urls = [tag.text for tag in soup.find_all('loc')]
        logging.info(f"Successfully extracted {len(urls)} URLs from the sitemap.")
        return urls
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching or parsing sitemap: {e}")
        return []

def scrape_and_clean_page(session: requests.Session, url: str) -> Optional[str]:
    # (This function does not need any changes)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            element.decompose()
        main_content = soup.find('main')
        text = main_content.get_text(separator=' ', strip=True) if main_content else soup.body.get_text(separator=' ', strip=True)
        return ' '.join(text.split())
    except requests.exceptions.RequestException:
        return None

def chunk_text(text: str, source_url: str, text_splitter: RecursiveCharacterTextSplitter) -> List[Dict[str, str]]:
    # (This function does not need any changes)
    if not text:
        return []
    chunks = text_splitter.create_documents([text], metadatas=[{"source": source_url}])
    return [{'source': chunk.metadata['source'], 'text': chunk.page_content} for chunk in chunks]

def process_and_upsert_batch(batch: List[Dict[str, str]], model: SentenceTransformer, index: Pinecone.Index):
    # (This function does not need any changes)
    if not batch:
        return
    texts_to_embed = [doc['text'] for doc in batch]
    embeddings = model.encode(texts_to_embed, show_progress_bar=False).tolist()
    
    vectors_to_upsert = []
    for i, doc in enumerate(batch):
        vec_id = str(uuid.uuid4())
        metadata = {"text": doc['text'], "source": doc['source']}
        vectors_to_upsert.append({"id": vec_id, "values": embeddings[i], "metadata": metadata})
        
    try:
        index.upsert(vectors=vectors_to_upsert)
    except Exception as e:
        logging.error(f"Error upserting batch to Pinecone: {e}")

# --- Main Execution Logic (No changes needed here) ---

def main():
    """Main function to run the entire data ingestion pipeline."""
    logging.info("--- Initializing Services ---")

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY) # Now using the variable loaded from .env
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            logging.info(f"Index '{PINECONE_INDEX_NAME}' not found. Creating it now...")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric='cosine',
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
            logging.info(f"Index '{PINECONE_INDEX_NAME}' created successfully.")
        index = pc.Index(PINECONE_INDEX_NAME)
        logging.info(f"Successfully connected to Pinecone index '{PINECONE_INDEX_NAME}'.")
        logging.info(f"Initial index stats: {index.describe_index_stats()}")
    except Exception as e:
        logging.critical(f"Fatal: Failed to connect to Pinecone. Exiting. Error: {e}")
        return

    # ... The rest of the main function is identical ...
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    logging.info(f"Embedding model '{EMBEDDING_MODEL_NAME}' and text splitter initialized.")
    
    with requests.Session() as session:
        all_page_urls = get_urls_from_sitemap(session, SITEMAP_URL)
        urls_to_process = all_page_urls[:URL_PROCESS_LIMIT] if URL_PROCESS_LIMIT else all_page_urls
        logging.info(f"Starting to process {len(urls_to_process)} URLs.")

        batch_buffer = []
        total_chunks_upserted = 0

        for url in tqdm(urls_to_process, desc="Scraping and Processing URLs"):
            cleaned_content = scrape_and_clean_page(session, url)
            if cleaned_content:
                page_chunks = chunk_text(cleaned_content, url, text_splitter)
                batch_buffer.extend(page_chunks)
            
            if len(batch_buffer) >= BATCH_SIZE:
                process_and_upsert_batch(batch_buffer, embedding_model, index)
                total_chunks_upserted += len(batch_buffer)
                batch_buffer.clear()
                logging.info(f"Upserted a batch. Total chunks so far: {total_chunks_upserted}")

            time.sleep(0.25)

        if batch_buffer:
            logging.info(f"Processing the final batch of {len(batch_buffer)} chunks...")
            process_and_upsert_batch(batch_buffer, embedding_model, index)
            total_chunks_upserted += len(batch_buffer)

    logging.info("\n--- Pipeline Complete ---")
    logging.info(f"Total chunks created and upserted: {total_chunks_upserted}")
    logging.info(f"Final Pinecone index stats: {index.describe_index_stats()}")

if __name__ == "__main__":
    main()