# Changi Airport AI Chatbot ✈️

This project is a sophisticated Retrieval-Augmented Generation (RAG) chatbot designed to answer questions about Singapore Changi Airport and Jewel Changi Airport. It leverages a modern tech stack to provide accurate, context-aware answers based on scraped website content.

The application consists of a backend REST API built with FastAPI and a simple user interface built with Streamlit. It is fully containerized with Docker for easy deployment and portability.

## ✨ Key Features

-   **Accurate, Context-Aware Answers:** Uses a RAG pipeline to ground responses in factual website data, preventing hallucinations.
-   **REST API Backend:** A robust FastAPI server that exposes a simple `/ask` endpoint for easy integration.
-   **Vector Search:** Employs Sentence Transformers for creating embeddings and Pinecone as a vector database for efficient similarity search.
-   **LLM Integration:** Powered by Google's Gemini family of models for natural language generation.
-   **Simple UI:** A user-friendly chat interface built with Streamlit for demonstration and interaction.
-   **Dockerized:** The entire backend is containerized with Docker, ensuring a consistent and reproducible environment.

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20.0-FF4B4B?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=for-the-badge&logo=docker)
![Pinecone](https://img.shields.io/badge/Pinecone-3.0-0077B5?style=for-the-badge&logo=pinecone)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google)

## 🏗️ Architecture

The application follows a standard client-server architecture. The Streamlit UI acts as a client that communicates with the FastAPI backend via a REST API. The backend handles the complex logic of retrieving context from the vector database and generating a response with the LLM.

```
+----------------+      +---------------------+      +------------------------+
|                |      |                     |      |                        |
|   User         +----->+   Streamlit UI      +----->+    FastAPI Backend     |
| (Browser)      |      | (chatbot_ui.py)     |      |       (main.py)        |
|                |      |                     |      |                        |
+----------------+      +----------+----------+      +-----------+------------+
                                  |                           |
                                  |                           | (Vector Search)
                                  |                           |
                                  |                           v
                                  |                      +----+-----+
                                  |                      | Pinecone |
                                  |                      +----------+
                                  |                           |
                                  |                           | (Prompt + Context)
                                  |                           |
                                  |                           v
                                  |                      +----+----+
                                  |                      | Gemini  |
                                  |                      +---------+
                                  |                           |
                                  |                           | (Final Answer)
                                  +---------------------------+
                                  |
                                  v
                             (Display to User)

```

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for running with Docker)
-   Git

### 1. Clone the Repository

```bash
git clone https://github.com/sainiakhil/LLM-RAG-Chatbot.git
cd LLM-RAG-Chatbot
```

### 2. Set Up Environment Variables

This project requires API keys for Pinecone and Google. These are managed using a `.env` file.

-   Create a new file named `.env` in the root of the project.
-   **This file is listed in `.gitignore` and should never be committed to source control.**

-   Add your keys to the `.env` file, formatted exactly like this (no spaces around the `=`):

    ```.env
    # .env.example - Copy this to a new .env file and add your keys
    PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

### 3. Install Dependencies

It is highly recommended to use a Python virtual environment.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

## 🏃 Running the Application

The application has two parts: the backend API and the frontend UI. They must be run in separate terminals.

### 1. Run the FastAPI Backend

In your first terminal (with the virtual environment activated):

```bash
python -m uvicorn main:app --reload
```

The API server will start on `http://127.0.0.1:8000`. You can see the auto-generated API documentation at `http://127.0.0.1:8000/docs`.

### 2. Run the Streamlit UI

In a **second terminal** (with the virtual environment activated):

```bash
streamlit run chatbot_ui.py
```

A new tab should automatically open in your browser with the chatbot interface. You can now start asking questions!

