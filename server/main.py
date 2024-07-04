import os
import time
from typing import Annotated
from fastapi import FastAPI, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from embed import create_embedding
from clients import vector_client
from llm import create_chat, PROMPT
from threading import Lock

embed_lock = Lock()
llm_lock = Lock()

app = FastAPI(
    title="Aerospike Vector RAG Demo",
    openapi_url=None, 
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rest/v1/chat/")
async def create_chat_completion(text: Annotated[str, Form()]):
    with embed_lock:
        embedding = create_embedding(text, "query")
    start = time.time()
    results = vector_search(embedding, 5)
    time_taken = time.time() - start

    context = ""
    docs = {}
    for result in results:
        context += f"{result.fields['content']}\n\n"
        docs[result.fields["title"]] = result.fields["url"]
                
    return StreamingResponse(
        stream_response(
            PROMPT.format(question=text, context=context),
            time_taken, 
            docs
        ), 
        media_type="text"
    )

def vector_search(embedding, count=5):
    return vector_client.vector_search(
        namespace="rag-vector",
        index_name=os.getenv("AVS_INDEX_NAME"),
        query=embedding,
        limit=count,
        field_names=["title", "url", "content"]
    )

def stream_response(prompt, time_taken, docs):
    yield f"_Query executed in {round(time_taken * 1000, 5)} ms_\n\n"
    yield f"The following documents will be used to provide context:\n\n"
    
    for key in docs:
        yield f"- [{key}]({docs[key]})\n"
    
    if llm_lock.locked():
        time.sleep(.5)
        yield "\nWaiting for slot...\n\n"

    with llm_lock:
        time.sleep(.5)
        yield "\nGenerating a response...\n\n"
        
        try:
            response = create_chat(prompt)
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred, please try again."
            )
    
    return