import os
from openai import OpenAI

model = OpenAI(
    api_key=os.getenv("OPEN_AI_API_KEY"),
)

PROMPT = '''\
You are a helpful assistant answering questions about the Aerospike NoSQL database.
Using the following context, answer the question.
If you are unable to answer the question, ask for more information.

Context: {context}
Question: {question}
'''

def create_chat(prompt):
    return model.chat.completions.create(
        model=os.getenv("OPEN_AI_MODEL"),
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )