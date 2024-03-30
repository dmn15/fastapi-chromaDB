import chromadb
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from main import get_dataframe
from loguru import logger

app = FastAPI()


class Query(BaseModel):
    query_text: str


df = get_dataframe()

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name='first')
documents = df['Documents'].tolist()
metadata = [{'item_id': str(i)} for i in range(1, 2001)]
ids = [str(i) for i in range(1, 2001)]
collection.add(
    documents=documents,
    metadatas=metadata,
    ids=ids
)


@app.get('/')
def index(name: str):
    return f'hello {name}, Welcome to document Retrieval Web APP'


app = FastAPI()


@app.post("/add_document")
def add_document(id: str, collection_name: str, document: str):
    filename = f"{id}_{collection_name}"

    if filename in documents:
        raise HTTPException(status_code=400, detail="Document already exists")

    try:
        chroma_collection = chroma_client.get_or_create_collection(name=collection_name)

        chroma_collection.add(
            documents=[document],
            metadatas=[{'file_name': filename}],
            ids=[filename]
        )

        return {"message": "Document added successfully", "filename": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


# -----------------------------------------------------------------------------------------------------------------

@app.post("/retrieve_documents")
async def retrieve_documents(query: Query, collection_name: str):
    try:
        chroma_collection = chroma_client.get_or_create_collection(name=collection_name)

        results = chroma_collection.query(
            query_texts=[query.query_text],
            n_results=5,
        )

        # Extract and return relevant information from the results
        response_data = [
            {
                "item_id": results['ids'][0][i],
                "distance": results['distances'][0][i],
                "metadata": results['metadatas'][0][i],
                "Document": results['documents'][0][i],
            }
            for i in range(len(results['ids'][0]))
        ]

        return {"results": response_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_collections")
def list_collections():
    try:
        all_collections = chroma_client.list_collections()
        return {"collections": all_collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("API:app", host='127.0.0.1', port=8000, reload=True)
