#-------------------------------------with text document-------------------------
#-----------------------------
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import chromadb
import uvicorn

chromaDB = chromadb.Client()

app = FastAPI()


class DocumentInfo(BaseModel):
    Department: str
    TechStack: str
    Document: str


# File to store added documents
file_path = "added_documents.txt"


def load_documents_from_file():
    try:
        with open(file_path, "r") as file:
            data = file.read()
        return data
    except FileNotFoundError:
        return ""


def save_documents_to_file(data):
    with open(file_path, "a") as file:
        file.write(data)


def document_exists_in_file(department: str, tech_stack: str):
    existing_data = load_documents_from_file()
    return f"Department: {department}, TechStack: {tech_stack}" in existing_data


def preprocess_document(document: str) -> str:
    return document.replace("\n\n", "\\n\\n").replace("\n", "\\n")


@app.post("/add_document")
def add_document(document_info: DocumentInfo):
    try:
        department = document_info.Department
        tech_stack = document_info.TechStack
        document = preprocess_document(document_info.Document)

        if document_exists_in_file(department, tech_stack):
            raise HTTPException(status_code=400, detail="Document already exists")

        collection = chromaDB.get_or_create_collection(name=department)

        collection.add(
            documents=[document],
            metadatas=[{'item_ids': f"{tech_stack}_{department}"}],
            ids=[f"{tech_stack}_{department}"]
        )

        new_document_info = f"Department: {department}, TechStack: {tech_stack}, Document: {document}\n"
        save_documents_to_file(new_document_info)

        return {"message": "Document added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"the Unique file already exists: {str(e)}")


@app.post("/retrieve_documents")
def retrieve_documents(collection_name: str, query: str = Query(...)):
    try:
        # Get the collection
        collection = chromaDB.get_or_create_collection(name=collection_name)

        # Query the collection
        results = collection.query(
            query_texts=[query],
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
        all_collections = chromaDB.list_collections()
        return {"collections": all_collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("test:app", host='127.0.0.1', port=8000, reload=True)

# ----------------------------------------------------------------------with
# json-----------------------------------------

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import chromadb
import json
import uvicorn

chromaDB = chromadb.Client()

app = FastAPI()


class DocumentInfo(BaseModel):
    Department: str
    TechStack: str
    Document: str


# File to store added documents
file_path = "added_documents.json"


def load_documents_from_file():
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"documents": []}
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
        return {"documents": []}


def save_documents_to_file(data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


def document_exists_in_file(department: str, tech_stack: str, data):
    return any(
        entry["Department"] == department and entry["TechStack"] == tech_stack
        for entry in data["documents"]
    )


def preprocess_document(document: str) -> str:
    return document.replace("\n\n", "\\n\\n").replace("\n", "\\n")


@app.post("/add_document")
def add_document(document_info: DocumentInfo):
    try:
        department = document_info.Department
        tech_stack = document_info.TechStack
        document = document_info.Document

        existing_data = load_documents_from_file()

        if document_exists_in_file(department, tech_stack, existing_data):
            raise HTTPException(status_code=400, detail="Document already exists")

        collection = chromaDB.get_or_create_collection(name=department)

        collection.add(
            documents=[document],
            metadatas=[{'item_ids': f"{tech_stack}_{department}"}],
            ids=[f"{tech_stack}_{department}"]
        )

        new_document_info = {
            "Department": department,
            "TechStack": tech_stack,
            "Document": document,
        }

        existing_data["documents"].append(new_document_info)
        save_documents_to_file(existing_data)

        return {"message": "Document added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@app.post("/retrieve_documents")
def retrieve_documents(collection_name: str, query: str = Query(...)):
    try:
        collection = chromaDB.get_or_create_collection(name=collection_name)

        results = collection.query(
            query_texts=[query],
            n_results=5,
        )

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
        all_collections = chromaDB.list_collections()
        return {"collections": all_collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("test:app", host='127.0.0.1', port=8000, reload=True)
