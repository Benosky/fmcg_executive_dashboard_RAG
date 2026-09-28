# High-Performance Self-Hosted FMCG RAG System with PostgreSQL, Pgvector, Ollama, LangChain  and Python

In this project I set out to build a fully localized Retrieval-Augmented Generation (RAG) system for a Fast Moving Consumer Goods company (`Amker`) using open source tools and platforms. This document will guide you through the setting up and using of `PostgreSQL`, `pgvector` with Python, Docker, LangChain and Ollama's popular `nomic-embed-text` and efficient `qwen3:4b` models for embeddings and text generations. The answers generation for this RAG solution, as with others, is based on the retrieved context. In other words, the answers to the queries sent to the RAG systems will not go beyond the context of the documents fed into the Pgvector db from where the answers are retrieved. Taking advantage of the full power of PostgreSQL the raw text were already extracted from their various sources, preprocessed and loaded to a table in the same PostgreSQL database as the pgvectors table to enhance operational efficiency.


## YouTube Quick Demo
You can watch the full tutorial here on [YouTube](https://youtu.be).


## Pgvector Documentation

For more information about using PostgreSQL, Pgvector AI RAG applications see the following resources:

- [Blog Post: PostgreSQL and Pgvector: Now Faster Than Pinecone, 75% Cheaper, and 100% Open Source](https://www.timescale.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost/)
- [Blog Post: RAG Is More Than Just Vector Search](https://www.timescale.com/blog/rag-is-more-than-just-vector-search/)
- [Build a Local RAG Pipeline With Ollama + pgvector — No API Keys, No Cloud](https://dev.to/signal-weekly/build-a-local-rag-pipeline-with-ollama-pgvector-no-api-keys-no-cloud-1h8a)


## Why Self-Hosted RAG Systems?

Here are five key reasons why companies prefer self-hosted RAG systems approach:

**- Data Privacy and Security:** Keeping the RAG system local or self-hosted ensures that sensitive corporate data, intellectual property, and customer information never leave the company's secure infrastructure or feed public AI models.

**- Elimination of Hallucinations:** By anchoring the AI's responses strictly within verified internal documents—such as wikis, HR policies, and technical manuals—the system provides highly accurate answers and minimizes the risk of generating false information.

**- Contextual Relevance:** Public AI models lack insight into a specific company's internal jargon, project histories, and unique workflows. A slef-hosted company-wide RAG system tailors answers specifically to the organization's unique operational context.

**- Cost Efficiency:** Querying commercial LLM APIs repeatedly with massive enterprise documents can quickly become cost-prohibitive. Local implementations allow companies to manage data processing costs predictably at scale.

**- Source Traceability:** Local RAG systems typically provide citations or direct links to the internal documents used to generate an answer, allowing employees to audit facts and verify the source material easily.



## Why Use Pgvector for RAG?

Using PostgreSQL with pgvector simplifies your Retrieval-Augmented Generation (RAG) architecture by keeping vector data and application records inside a single system:

**- Single Source of Truth:** Store your text chunks, metadata, and vector embeddings together in one table.
**- Familiar SQL:** Run standard joins, filters, and keyword searches alongside vector similarity queries.
**- Lower Operations Cost:** Avoid setting up, paying for, and maintaining a separate vector database.


## Prerequisites

- Docker
- Homebrew
- Python 3.10.6
- Postgresql@17
- Ollama
- PostgreSQL GUI client (eg., PgAdmin, DBeaver, etc)

## Steps

1. Install and test the Postgresql@17 using Homebrew.
2. Connect to the database using a PostgreSQL GUI client to be sure it is well set up.
3. Create a stand alone Python script to extract the raw input data from a staging csv file, process the data  and load it to a table in the postgres db.
4. Set up Docker environment
5. Create a Python script to insert the preprocess documents into the Pgvector instance for vector, semantic and contextual embeddings using Ollama `nomic-embed-text` model.
6. Create a Python function to expose the query endpoints for accepting questions from and providing responses to the end users.
7. Test the endpoint to ensure it is working as expected.


## Detailed Instructions (On Macos)

### 1. Install and test the Postgresql@17 package using Homebrew

`brew install Postgresql@17`

- Start Postgresql@17 as a background service

`brew services start postgresql@17`

- Create a Custom Superuser with a Password

```bash
psql postgres
```

- Inside the interactive prompt (postgres=#), execute the SQL command:

```sql
CREATE ROLE postgres WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'password';
```

- Exit the psql prompt (type \q and press Enter to exit the PostgreSQL prompt.)

```sql
\q
```

- Verify Your Connection

```bash
# Connect using the postgres user
psql -U postgres -d postgres
```

### 2. Connect to the database using a PostgreSQL GUI client (DBeaver) to be sure it is properly set up.

- Open client
- Create a new connection with the following details:
  - Host: localhost
  - Port: 5432
  - User: postgres
  - Password: password
  - Database: postgres


### 3.  Create and run a stand alone Python script to extract the raw input data from a staging csv file, process the data  and load it to a table in the postgres db.

```bash
python prep_docs.py
```


### 4. Set up Docker environment

Create a `docker-compose.yml` file with the following content:

```yaml
# version: '3.8'

services:
  # Database Service
  postgres:
    image: pgvector/pgvector:pg17
    container_name: faq_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql 
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Ollama Local Model Server (Stock Engine)
  ollama:
    image: ollama/ollama:latest
    container_name: faq_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD-SHELL", "ollama --version || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 3

  # # Dedicated Download Worker (This took too long to run, so I pulled the models into the container on bash)
  # ollama-pull-models:
  #   image: ollama/ollama:latest
  #   container_name: faq_ollama_loader
  #   volumes:
  #     - ollama_data:/root/.ollama
  #   depends_on:
  #     ollama:
  #       condition: service_healthy
  #   entrypoint: /bin/sh
  #   command:
  #     - "-c"
  #     - |
  #       echo "Connecting to Ollama server..."
  #       until ollama list >/dev/null 2>&1; do sleep 1; done
  #       echo "=== Pulling nomic-embed-text ==="
  #       ollama pull nomic-embed-text
  #       echo "=== Pulling qwen3:4b ==="
  #       ollama pull qwen3:4b
  #       echo "=== All weights pulled successfully ==="

  # FastAPI Web Application Service
  web:
    build: .
    container_name: faq_rag_api
    ports:
      - "8000:8000"
    environment:
      - HOST=postgres
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_healthy
      # ollama-pull-models:
      #   condition: service_completed_successfully # Safely blocks API boot until files land
volumes:
  postgres_data:
  ollama_data:
```

Run the Docker to create the containers for the `postgres` and `ollama` services:

```bash
docker compose up --build postgres ollama
```

Pull the ollama models into the created ollama container:

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull tinyllama
```

Run the Docker to create the containers for the `web` services to expose the :

```bash
docker compose up --build postgres web
```


### 5. Create a Python script to insert the preprocess documents into the Pgvector instance for vector, semantic and contextual embeddings using Ollama `nomic-embed-text` model.

See `main.py` 

### 6. Create a Python function to expose the query endpoints for accepting questions from and providing responses to the end users.

See `main.py`.

### 7. Test the endpoint to ensure it is working as expected.

![Alt text]("RAG_Query.png")

![Alt text]("RAG_Response.png")


