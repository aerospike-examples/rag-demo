import llama_cpp

model = llama_cpp.Llama(
    model_path="../../Models/gemma-7b-it/ggml-model-f32.gguf",
    chat_format="gemma",
    n_ctx=0,
    n_gpu_layers=-1
)

PROMPT = '''\
You are a helpful assistant answering questions about the Aerospike NoSQL database.
Using the following context, answer the question.
If you are unable to answer the question, ask for more information.

Context: {context}
Question: {question}
'''

def create_chat(prompt):
    return model.create_chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
        repeat_penalty=1.0,
        temperature=0
    )