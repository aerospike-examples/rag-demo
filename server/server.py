from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import time
from config import Config
from data_encoder import encoder
from proximus_client import proximus_client
from llm import create_chat, PROMPT

origins = [
    "http://localhost:8080"
]

app = FastAPI(
    title="Proximus RAG Demo",
    openapi_url=None, 
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBasic()

def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_uname = secrets.compare_digest(credentials.username.encode("utf8"), Config.BASIC_AUTH_USERNAME.encode("utf8"))
    correct_pword = secrets.compare_digest(credentials.password.encode("utf8"), Config.BASIC_AUTH_PASSWORD.encode("utf8"))
    
    if not (correct_uname and correct_pword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or Password incorrect",
            headers={"WWW-Authenticate": "Basic"}
        )
    else:
        return True

@app.post("/rest/v1/chat/")
async def create_chat_completion(text: Annotated[str, Form()], logged_in: Annotated[bool, Depends(login)] = False):
    if logged_in:
        embedding = encoder(text, "query")
        start = time.time()
        results = vector_search(embedding, 6)
        time_taken = time.time() - start

        context = ""
        docs = {}
        for result in results:
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

@app.get("/")
async def root(logged_in: Annotated[bool, Depends(login)] = False):
    if logged_in:
        return FileResponse('dist/index.html')

def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    bins = ("title", "url", "idx", "content")
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