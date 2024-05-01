from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import requests
import time
from config import Config
from data_encoder import encoder
from proximus_client import proximus_client
from llm import create_chat, PROMPT
from threading import Lock

origins = [
    "https://vector-rag-aerospike.netlify.app",
    "https://vector-rag.aerospike.com"
]

embed_lock = Lock()
llm_lock = Lock()

app = FastAPI(
    title="Proximus RAG Demo",
    openapi_url=None, 
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    url = "https://vector-rag-aerospike.netlify.app/.netlify/functions/check_user"
    response = requests.get(url, headers={"Authorization": "Bearer " + token})
    if not response.ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    else:
        return True

@app.post("/rest/v1/chat/")
async def create_chat_completion(text: Annotated[str, Form()], auth: Annotated[bool, Depends(get_auth)] = False):
    if auth:
        with embed_lock:
            embedding = encoder(text, "query")
        start = time.time()
        results = vector_search(embedding, 5)
        time_taken = time.time() - start

        context = ""
        docs = {}
        sorted_results = sorted(results, key=lambda result: result.distance)
        for result in sorted_results:
            context += f"{result.bins['content']}\n\n"
            docs[result.bins["title"]] = result.bins["url"]
                    
        return StreamingResponse(
            stream_response(
                PROMPT.format(question=text, context=context),
                time_taken, 
                docs
            ), 
            media_type="text"
        )

def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    bins = ("title", "url", "content")
    return proximus_client.vectorSearch(
        Config.PROXIMUS_NAMESPACE,
        Config.PROXIMUS_INDEX_NAME,
        embedding,
        count,
        None,
        *bins,
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
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred, please try again."
            )
    
    return