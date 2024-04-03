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
from llm import create_chat

PROMPT = '''\
You are a helpful assistant answering questions about the Aerospike NoSQL database.
Using the following context, answer the question.
If you are unable to answer the question, ask for more information.

Context: {context}
Question: {question}
'''

app = FastAPI()
security = HTTPBasic()

app.mount("/static", StaticFiles(directory="dist"), name="static")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        documents = {}
        for result in results:
            if documents.get(result.bins['title']):
                documents[result.bins['title']]["content"].insert(result.bins["idx"], result.bins["content"])
            else:        
                documents[result.bins['title']] = {"url": result.bins['url'], "content": [result.bins["content"]]}
        
        context = ""
        docs = []
        for idx, key in enumerate(documents):
            if idx < 3:
                context += " ".join(documents[key]["content"])
                docs.append({"title": key, "url": documents[key]["url"]})
        
        return StreamingResponse(stream_response(PROMPT.format(question=text, context=context), time_taken, docs), media_type="text")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized!"
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
    
    for doc in docs:
        yield f"- [{doc['title']}]({doc['url']})\n"
    
    time.sleep(.5)
    yield "\nGenerating a response...\n\n"

    try:
        response = create_chat(prompt)
        for chunk in response:
            content = chunk["choices"][0]["delta"].get("content")
            if content:
                yield content
    
    except Exception as e:
        return "An error occurred, please try again.\n{e}".format(e), 400 
    
    return