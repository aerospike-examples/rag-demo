import time
from flask import request, send_file

from config import Config
from data_encoder import encoder
from server import app
from proximus_client import proximus_client
from llm import model

PROMPT = '''\
You are a helpful assistant answering questions about the Aerospike NoSQL database.
Using the following context, answer the question.
If you are unable to answer the question, ask for more information.

Context: {context}
Question: {question}
'''

@app.route("/")
def index_static():
    return send_file("dist/index.html")

@app.route("/rest/v1/chat", methods=["POST"])
def search():
    text = request.form["text"]
    if text:
        embedding = encoder(text, "query")
        start = time.time()
        results = vector_search(embedding[0].tolist(), 6)
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
        
        return stream_response(PROMPT.format(question=text, context=context), time_taken, docs), {"Content-Type": "text"}
    else:
        return "No prompt provided. Please provide a prompt.", 400

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
        response = model.create_chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ], 
            stream=True,
            repeat_penalty=1.0,
            temperature=0
        )
    except Exception as e:
        return "An error occurred, please try again.\n{e}".format(e), 400 

    for chunk in response:
        content = chunk["choices"][0]["delta"].get("content")
        if content:
            yield content
    return