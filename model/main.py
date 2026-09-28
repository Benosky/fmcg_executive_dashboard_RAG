import os
import json  # Fixed missing import
from pydantic import BaseModel 
from fastapi import FastAPI, HTTPException 
from fastapi.responses import StreamingResponse 
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
# from langchain_community.document_loaders import PostgreSQLLoader 
from langchain_ollama import OllamaEmbeddings, ChatOllama 
# from langchain_postgres import PostgresVector 
from langchain_core.documents import Document
from sqlalchemy import create_engine
from langchain_postgres.vectorstores import PGVector

import uvicorn
import pandas as pd

# Initialize FastAPI app
app = FastAPI(title="FAQ RAG API", version="1.0")

# 1. Configuration & Global State

USERNAME = 'postgres'      
PASSWORD = 'postgres'              
# HOST = 'localhost'
PORT = '5432'
DATABASE = 'postgres' 

# Read parameters passed from docker-compose.yml
HOST = os.getenv('HOST', 'localhost') 
OLLAMA_BASE_URL = os.getenv('OLLAMA_HOST', 'http://localhost:11434') 

CONNECTION_STRING = f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
COLLECTION_NAME = "faq_rag_collection"


# CONNECTION_STRING = "postgresql+psycopg://postgres:password@localhost:5432/mydatabase"
# COLLECTION_NAME = "local_rag_collection"

# 2. Lazy Initialization of Models and Vector Store
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

# llm = ChatOllama(model="llama3.2", temperature=0)
llm = ChatOllama(
    model="tinyllama", 
    temperature=0, 
    base_url=OLLAMA_BASE_URL
)

# vector_store = PostgresVector(
#     connection=CONNECTION_STRING,
#     embeddings=embeddings,
#     collection_name=COLLECTION_NAME,
#     use_jsonb=True
# )

# 3. Pydantic Schemas for Requests/Responses
class QueryRequest(BaseModel):
    question: str
    top_k: int = 2

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]

class IngestResponse(BaseModel):
    status: str
    documents_ingested: int


# connection = f"postgresql+psycopg://postgres:postgres@{HOST}:5432/postgres"
connection = "postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
# query = "SELECT id, category, contents FROM faq_records;"

def docs_ids():
    # 1. Establish database connection
    # connection = f"postgresql+psycopg://postgres:postgres@{HOST}:5432/postgres"
    query = "SELECT id, contents, metadata FROM policy_sop_guide_docs;"
    engine = create_engine(connection)

    # 2. Read using a SQL query
    df_query = pd.read_sql(query, engine)

    documents = []
    ids = []
    for doc, id, met in zip(df_query.contents, df_query.id, df_query.metadata):
        document = Document(
                page_content=doc, metadata=met #{"category": cat}
            )
        documents.append(document)
        ids.append(id)
    return {'documents':documents, 'ids':ids}

    

# # 4. RAG Ingestion Endpoint
# @app.post("/ingest", response_model=IngestResponse, tags=["Data Management"])
# async def ingest_database_data():
#     try:
#         # connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
#         # query = "SELECT id, category, contents FROM faq_records;"

#         # # 1. Establish database connection
#         # engine = create_engine(connection)

#         # # 2. Read using a SQL query
#         # df_query = pd.read_sql(query, engine)

#         # documents = []
#         # ids = []
#         # for doc, id, cat in zip(df_query.contents, df_query.id, df_query.category):
#         #     document = Document(
#         #             page_content=doc, metadata={"category": cat}
#         #         )
#         #     documents.append(document)
#         #     ids.append(id)

#         # vector_store = PGVector(
#         #     embeddings=OllamaEmbeddings(model="nomic-embed-text"),
#         #     collection_name=collection_name,
#         #     connection=connection,
#         #     use_jsonb=True,
#         # )

#         raw_documents = docs_ids()['documents'] #vector_store.add_documents(documents=documents, ids=ids)

#         # query = "SELECT id, category, contents FROM faq_records;"
#         # loader = PostgreSQLLoader(
#         #     connection_string=CONNECTION_STRING, 
#         #     query=query, 
#         #     page_content_column="contents", 
#         #     metadata_columns=["id", "category"]
#         # )
#         # raw_documents = loader.load()
#         if not raw_documents:
#             return {"status": "success", "documents_ingested": 0}

#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         docs = text_splitter.split_documents(raw_documents)

#         ids = docs_ids()['ids']
#         # Better alternative to drop_tables() to clear the current collection safe and clean
#         vector_store = vector_store
#         vector_store.delete(delete_all=True) 
#         # vector_store.add_documents(docs)
#         vector_store.add_documents(documents=docs, ids=ids)
        
#         return {"status": "success", "documents_ingested": len(docs)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# def ingest_database_data():

vector_store = PGVector(
        embeddings=OllamaEmbeddings(model="nomic-embed-text"),
        collection_name=COLLECTION_NAME,
        connection=connection,
        use_jsonb=True,
    )
try:
    # connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    raw_documents = docs_ids()['documents'] #vector_store.add_documents(documents=documents, ids=ids)
    if not raw_documents:
        print("status: success, documents_ingested: 0")
    else:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(raw_documents)

        ids = docs_ids()['ids']
        # Better alternative to drop_tables() to clear the current collection safe and clean
        # vector_store = vector_store
        vector_store.delete(delete_all=True) 
        # vector_store.add_documents(docs)
        vector_store.add_documents(documents=docs, ids=ids)
        vector_store._engine.dispose()
        print(f"status: success, documents_ingested: {len(docs)}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# 5. RAG Query Endpoint
@app.post("/", tags=["RAG Interface"])
async def query_rag(request: QueryRequest):
    try:
        # vector_store = vector_store
        # connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
        # vector_store = PGVector(
        #     embeddings=OllamaEmbeddings(model="nomic-embed-text"),
        #     collection_name=COLLECTION_NAME,
        #     connection=connection,
        #     use_jsonb=True,
        # )
        
        retriever = vector_store.as_retriever(search_kwargs={"k": request.top_k})
        relevant_docs = retriever.invoke(request.question)
        sources = [doc.metadata for doc in relevant_docs]
        
        context = "\n\n".join(doc.page_content for doc in relevant_docs)
        
        template = """Answer the question based only on the following context: {context} Question: {question} Answer:"""
        prompt = ChatPromptTemplate.from_template(template)
        rag_chain = prompt | llm | StrOutputParser()

        async def text_stream_generator():
            async for chunk in rag_chain.astream({"context": context, "question": request.question}):
                yield chunk

        headers = {
            "X-RAG-Sources": json.dumps(sources), # Will now run successfully
            "Access-Control-Expose-Headers": "X-RAG-Sources" 
        }
        
        return StreamingResponse(
            text_stream_generator(), 
            media_type="text/plain", 
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming query failed: {str(e)}")

# To run locally via script directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# @app.post("/query", tags=["RAG Interface"])
# async def query_rag_stream(request: QueryRequest):
#     """
#     Streams the LLM response word-by-word. 
#     Source metadata is attached to the HTTP Response Headers.
#     """
#     try:
#         retriever = vector_store.as_retriever(search_kwargs={"k": request.top_k})
        
#         # 1. Fetch related context chunks asynchronously
#         relevant_docs = await retriever.ainvoke(request.question)
#         sources = [doc.metadata for doc in relevant_docs]
#         context = "\n\n".join(doc.page_content for doc in relevant_docs)
        
#         # 2. Build the LLM chain
#         template = """Answer the question based only on the following context:
#         {context}

#         Question: {question}
#         Answer:"""
#         prompt = ChatPromptTemplate.from_template(template)
#         rag_chain = prompt | llm | StrOutputParser()
        
#         # 3. Define an asynchronous generator to yield chunks of text
#         async def text_stream_generator():
#             async for chunk in rag_chain.astream({"context": context, "question": request.question}):
#                 yield chunk

#         # 4. Return the stream. Metadata is embedded into custom HTTP headers.
#         # We URL-encode or safely dump JSON string for the headers.
#         headers = {
#             "X-RAG-Sources": json.dumps(sources),
#             "Access-Control-Expose-Headers": "X-RAG-Sources"  # Crucial for browser-based frontends
#         }
        
#         return StreamingResponse(
#             text_stream_generator(), 
#             media_type="text/plain", 
#             headers=headers
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Streaming query failed: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)