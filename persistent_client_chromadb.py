from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from test4 import create_and_add_documents
import uvicorn
import os
import pandas as pd
import chromadb
from chromadb.config import Settings

app = FastAPI()

import os
import chromadb
from chromadb.config import Settings
import pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, 'data1')
chroma_client = chromadb.PersistentClient(path=DB_PATH, settings=Settings(allow_reset=True, anonymized_telemetry=False))
sample_collection = chroma_client.get_or_create_collection(name="sample_collection")


class QueryInput(BaseModel):
    query_text: str
    n_results: int = 3


class QueryResultItem(BaseModel):
    item_id: str
    document: str


class QueryResult(BaseModel):
    results: list[QueryResultItem]


@app.post("/query_documents", response_model=QueryResult)
def query_documents(query_input: QueryInput):
    try:
        query_text = query_input.query_text
        n_results = query_input.n_results

        query_result = sample_collection.query(query_texts=[query_text], n_results=n_results)

        result_documents = query_result["documents"][0]
        result_ids = query_result["ids"][0]

        response_data = []
        for doc_id,document in zip(result_ids,result_documents):
            response_data.append({
                "item_id": doc_id,
                "document": document,
            })

        return {"results": response_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query documents: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("test5:app", host='127.0.0.1', port=8000, reload=True)
