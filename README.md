
# Changi Airport AI Chatbot ✈️

This project is a sophisticated, multi-service chatbot application designed to answer questions about Singapore Changi Airport and Jewel Changi Airport. It leverages a modern, decoupled architecture with a FastAPI backend and a Streamlit frontend, both fully containerized with Docker.

The chatbot provides accurate, context-aware answers by using a Retrieval-Augmented Generation (RAG) pipeline, grounding its responses in factual data scraped from the official websites.

## ✨ Key Features

-   **Decoupled Frontend/Backend:** A scalable, professional architecture with a separate API and user interface.
-   **Accurate RAG Pipeline:** Grounds LLM responses in factual website data to prevent hallucinations.
-   **REST API Backend:** A robust FastAPI server exposing a simple `/ask` endpoint for easy integration.
-   **Vector Search:** Employs Sentence Transformers for embeddings and Pinecone as a vector database for efficient search.
-   **Interactive UI:** A user-friendly, real-time chat interface built with Streamlit.
-   **Fully Containerized:** Both the frontend and backend are Dockerized, ensuring consistent, reproducible environments for development and deployment.

## 🏗️ Project Architecture

The application consists of two independent services:

1.  **FastAPI Backend:** Handles all the heavy lifting—data processing, vector retrieval, and LLM interaction.
2.  **Streamlit UI:** A lightweight client that consumes the backend's REST API to provide a user interface.

```
+----------------+      +---------------------+      +------------------------+
|                |      |  Streamlit UI App   |      |    FastAPI Backend App |
|      User      +----->+  (in /Chatbot-UI)   +----->+   (in /FastAPI-Backend)|
|   (Browser)    |      | (Container 1)       |      |      (Container 2)     |
|                |      |                     |      |                        |
+----------------+      +---------------------+      +-----------+------------+
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

## 📂 Folder Structure

The project is organized into a monorepo with dedicated folders for each service.

```/
├── FastAPI-Backend/
│   ├── main.py             # The FastAPI application logic
│   ├── scrapper.py         # Script to scrape data (run separately)
│   ├── Dockerfile          # Instructions to build the backend image
│   ├── requirements.txt    # Python dependencies for the backend
│   └── .env                # (You must create this) For API keys
│
├── Chatbot-UI/
│   ├── chatbot_ui.py       # The Streamlit application UI
│   ├── Dockerfile          # Instructions to build the frontend image
│   └── requirements.txt    # Python dependencies for the frontend
│
├── .gitignore
└── README.md
```

## 🚀 Getting Started

Follow these instructions to set up and run both the backend and frontend services.

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20.0-FF4B4B?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=for-the-badge&logo=docker)
![Pinecone](https://img.shields.io/badge/Pinecone-3.0-0077B5?style=for-the-badge&logo=pinecone)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google)

### 1. Clone the Repository

```bash
git clone https://github.com/sainiakhil/LLM-RAG-Chatbot.git
cd LLM-RAG-Chatbot
```

### 2. Set Up Backend Environment Variables

The backend requires API keys to function.

-   Navigate to the backend folder: `cd FastAPI-Backend`
-   Create a new file named `.env`.
-   **This file is listed in `.gitignore` and should never be committed.**
-   Add your keys to the `.env` file, formatted exactly like this:

    ```.env
    PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

## 🏃 Running for Local Development

This approach is best for actively developing the code. You will need two separate terminals.

### Terminal 1: Run the FastAPI Backend

```bash
# Navigate to the backend directory
cd FastAPI-Backend

# Create and activate a Python virtual environment (recommended)
python -m venv .venv
# On Windows: .\.venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn main:app --reload
```

The API will be running at `http://127.0.0.1:8000`.

### Terminal 2: Run the Streamlit UI

```bash
# Navigate to the frontend directory
cd Chatbot-UI

# Create and activate a separate virtual environment (recommended)
python -m venv .venv
# On Windows: .\.venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

# Install frontend dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run chatbot_ui.py
```

The UI will be accessible at `http://127.0.0.1:8501`.

## 🐳 Running with Docker

This is the recommended way to run the application for a stable, production-like experience.

### 1. Build the Docker Images

You need to build an image for each service from its respective directory.

```bash
# Build the backend API image
cd FastAPI-Backend
docker build -t changi-chatbot-api .
cd ..

# Build the frontend UI image
cd Chatbot-UI
docker build -t changi-chatbot-ui .
cd ..
```

### 2. Run the Docker Containers

You will need two separate terminals to run the containers.

#### Terminal 1: Run the Backend Container

Navigate to the `FastAPI-Backend` folder to give the command access to your `.env` file.

```bash
cd FastAPI-Backend

# Run the container, securely passing the .env file
docker run --rm -p 8000:8000 --env-file .env changi-chatbot-api
```

The backend API is now running and accessible at `http://127.0.0.1:8000`.

#### Terminal 2: Run the Frontend Container

Make sure your `chatbot_ui.py` is pointing to the correct backend URL (`http://127.0.0.1:8000/ask`).

```bash
# Navigate to the root folder (or anywhere else)
# This command doesn't depend on local files

# Run the frontend container
docker run --rm -p 8501:8501 changi-chatbot-ui```

The Streamlit UI is now running and accessible at `http://127.0.0.1:8501`.

```


