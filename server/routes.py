import time
from flask import request, send_file

from config import Config
from data_encoder import encoder
from server import app
from proximus_client import proximus_client
from llm import model

@app.route("/")
def index_static():
    return send_file("dist/index.html")

@app.route("/rest/v1/chat", methods=["POST"])
def search():
    text = request.form["text"]
    if text:
        embedding = encoder(text, "search")
        start = time.time()
        results = vector_search(embedding.tolist(), 10)
        time_taken = time.time() - start

        documents = {}
        for result in results:
            if documents.get(result.bins['title']):
                documents[result.bins['title']]["content"].insert(result.bins["idx"], result.bins["content"])
            else:        
                documents[result.bins['title']] = {"url": result.bins['url'], "content": [result.bins["content"]]}
        
        context = ""
        for idx, key in enumerate(documents):
             if idx < 5:
                context += " ".join(documents[key]["content"])

        prompt = '''\
        Use the following context to answer this question about the Aerospike NoSQL database: {question}
        If the context does not help to answer the question, ask the user to restate the question.
        
        context: {context}
        '''.format(question=text, context=context)
        
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
        
        def streamRes():
            yield f"_Query executed in {round(time_taken, 5)} seconds_\n\n"
            yield f"The following documents will be used to provide context:\n\n"
            
            for key in documents:
                yield f"- [{key}]({documents[key]['url']})\n"
            
            time.sleep(.5)
            yield "\nGenerating a response...\n\n"

            for chunk in response:
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content
        return streamRes(), {"Content-Type": "text"}
    else:
        return "No text uploaded", 400

def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    # Execute kNN search over the dataset
    bins = ("title", "url", "idx", "content")
    return proximus_client.vectorSearch(
        Config.PROXIMUS_NAMESPACE,
        Config.PROXIMUS_INDEX_NAME,
        embedding,
        count,
        None,
        *bins,
    )
