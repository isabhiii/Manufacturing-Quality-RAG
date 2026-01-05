# Manufacturing Quality Assistant

A production oriented RAG system designed to reduce information retrieval time in manufacturing environments. This application allows engineers to upload technical documentation (SOPs, ISO standards, test procedures) and retrieve precise, cited answers via a natural language interface.

### Demo video file included:

![Project Demo](demo_video.mp4)

## Architecture

The system is built as a modular monorepo services architecture:

*   **Ingestion Pipeline**: Processes PDF documents, chunks text semantically, and generates embeddings using localized models.
*   **Vector Store**: Uses ChromaDB for dense vector retrieval, persisted locally for data privacy.
*   **RAG Orchestration**: Implements a custom retrieval pipeline using LangChain. It is model agnostic and currently configured to use Google Gemini 2.5 Flash for high speed technical reasoning.
*   **Backend API**: Fast and asynchronous REST API built with Python FastAPI. Handles document management and query processing.
*   **Frontend**: A clean, responsive user interface built with Streamlit, supporting bulk file uploads and side by side citation verification.
*   **Infrastructure**: Fully containerized using Docker and Docker Compose for consistent deployment across environments.

## Technical Stack

*   **Language**: Python 3.11
*   **Backend**: FastAPI, Uvicorn
*   **LLM Integration**: LangChain, Google Gemini API
*   **Vector Database**: ChromaDB
*   **Frontend**: Streamlit
*   **DevOps**: Docker, Docker Compose

## Setup and Installation

### Prerequisites

*   Docker Desktop installed and running.
*   A Google Cloud API Key with access to Gemini models.

### Configuration

1.  Clone this repository.
2.  Create a `.env` file in the root directory:

    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

### Running the Application

Execute the following command to build and start the services:

```bash
docker compose up --build
```

The services will be available at:

*   **Frontend**: http://localhost:8501
*   **Backend API Docs**: http://localhost:8000/docs

## Usage

1.  Navigate to the web interface.
2.  Use the sidebar to upload one or more PDF documents (e.g., machinery manuals or quality standards).
3.  Wait for the indexing confirmation.
4.  Ask technical questions in the chat window. The system will respond with specific answers and cite the exact source document and page number.

## License

MIT
