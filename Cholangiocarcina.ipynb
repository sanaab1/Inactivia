!pip install openai scikit-learn numpy

import os
import numpy as np
from getpass import getpass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from google.colab import userdata
from openai import OpenAI

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

source_1 = load_file("/content/Cholangiocarcinoma-lance.txt")
source_2 = load_file("/content/OnlineLibrary.txt")
source_3 = load_file("/content/ScienceDirect.txt")
all_sources_text = [source_1, source_2, source_3]
print("Sources loaded.")

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

chunks = []
for doc in all_sources_text:
    chunks.extend(chunk_text(doc))
print(f"Created {len(chunks)} chunks.")

vectorizer = TfidfVectorizer()
embeddings = vectorizer.fit_transform(chunks)
print("Embeddings created.")

def retrieve_chunks(query, top_k=3):
    query_embedding = vectorizer.transform([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_k_indices = np.argsort(similarities[0])[-top_k:][::-1]
    return [chunks[i] for i in top_k_indices]
os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY')
client = OpenAI()
def generate_answer(query):
    retrieved = retrieve_chunks(query)
    context = "\n\n".join(retrieved)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use the following context to answer the user query."
        },
        {
            "role": "user",
            "content": f"Context: {context}\n\nQuestion: {query}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content

user_query = input("What is your question about cholangiocarcinomia?: ")
answer = generate_answer(user_query)
print(f"\nFinal Answer:\n{answer}")
