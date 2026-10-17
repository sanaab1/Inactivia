import os
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

DATA_FILE = "note.txt"

def load_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find '{path}'.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

source_text = load_file(DATA_FILE)

def chunk_text(text, chunk_size=200, overlap=30):
    words = text.split()
    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

chunks = chunk_text(source_text)
vectorizer = TfidfVectorizer()
embeddings = vectorizer.fit_transform(chunks)

def retrieve_context(query, top_k=3):
    query_embedding = vectorizer.transform([query])
    similarities = cosine_similarity(query_embedding, embeddings)
    top_k_indices = np.argsort(similarities[0])[-top_k:][::-1]
    return "\n\n".join([chunks[i] for i in top_k_indices])

def might_be_question(text):
    return (
        bool(re.search(r'[?]\s*$', text)) or
        bool(re.match(r'^(who|what|when|where|why|how|which|whose|whom|can|could|would|should|do|does|did|is|are|was|were|will|has|have|had)\b', text, re.IGNORECASE))
    )

def scan_and_answer_file(text):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    results = []

    print("\n--- Scanning note.txt for Questions ---")
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        if might_be_question(sentence):
            print(f"\n[Detected Potential Question]: {sentence}")

            context_start = max(0, i - 3)
            context_end = min(len(sentences), i + 4)
            surrounding_context = " ".join(sentences[context_start:context_end])

            classifier_prompt = f"""Analyze this sentence in the context of the surrounding notes.

Surrounding Context:
"{surrounding_context}"

Sentence to analyze:
"{sentence}"

Determine if this sentence represents a genuine question that requires an explicit factual answer, or if it is merely rhetorical, transitional, or a title/heading.

Return JSON format:
{{"type": "genuine"}} or {{"type": "rhetorical"}}"""

            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": classifier_prompt}],
                    response_format={"type": "json_object"}
                )
                classification = json.loads(completion.choices[0].message.content)

                if classification.get("type") == "genuine":
                    print(" -> Status: GENUINE QUESTION. Retrieving context...")
                    retrieved_context = retrieve_context(sentence)

                    answer_prompt = f"""Answer the question using ONLY the provided context from note.txt. Format your entire answer as concise jot notes using bullet points. If the answer isn't in the context, say so concisely.

Context:
{retrieved_context}

Question: {sentence}
Answer (in jot notes):"""

                    ans_completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": answer_prompt}]
                    )
                    answer = ans_completion.choices[0].message.content
                    print(f" -> Answer:\n{answer}")
                    results.append({"question": sentence, "type": "genuine", "answer": answer})
                else:
                    print(" -> Status: Rhetorical / Skipped.")
            except Exception as e:
                print(f"Error processing question: {e}")

    return results

if __name__ == "__main__":
    qa_results = scan_and_answer_file(source_text)
    print(f"\nScan complete! Answered {len([r for r in qa_results if r['type'] == 'genuine'])} genuine questions from note.txt.")

# import os
# import re
# import json
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()
# client = OpenAI()

# def chunk_text(text, chunk_size=200, overlap=30):
#     words = text.split()
#     chunks = []
#     step = max(1, chunk_size - overlap)
#     for i in range(0, len(words), step):
#         chunk = " ".join(words[i:i + chunk_size])
#         if chunk:
#             chunks.append(chunk)
#     return chunks

# def might_be_question(text):
#     return (
#         bool(re.search(r'[?]\s*$', text)) or
#         bool(re.match(r'^(who|what|when|where|why|how|which|whose|whom|can|could|would|should|do|does|did|is|are|was|were|will|has|have|had)\b', text, re.IGNORECASE))
#     )

# def scan_and_answer_file(source_text):
#     chunks = chunk_text(source_text)
#     vectorizer = TfidfVectorizer()
#     embeddings = vectorizer.fit_transform(chunks)

#     def retrieve_context(query, top_k=3):
#         query_embedding = vectorizer.transform([query])
#         similarities = cosine_similarity(query_embedding, embeddings)
#         top_k_indices = np.argsort(similarities[0])[-top_k:][::-1]
#         return "\n\n".join([chunks[i] for i in top_k_indices])

#     sentences = re.split(r'(?<=[.?!])\s+', source_text)
#     results = []

#     print("\n--- Scanning document for Questions ---")
#     for i, sentence in enumerate(sentences):
#         sentence = sentence.strip()
#         if not sentence:
#             continue

#         if might_be_question(sentence):
#             print(f"\n[Detected Potential Question]: {sentence}")

#             context_start = max(0, i - 3)
#             context_end = min(len(sentences), i + 4)
#             surrounding_context = " ".join(sentences[context_start:context_end])

#             classifier_prompt = f"""Analyze this sentence in the context of the surrounding notes.

# Surrounding Context:
# "{surrounding_context}"

# Sentence to analyze:
# "{sentence}"

# Determine if this sentence represents a genuine question that requires an explicit factual answer, or if it is merely rhetorical, transitional, or a title/heading.

# Return JSON format:
# {{"type": "genuine"}} or {{"type": "rhetorical"}}"""

#             try:
#                 completion = client.chat.completions.create(
#                     model="gpt-4o-mini",
#                     messages=[{"role": "user", "content": classifier_prompt}],
#                     response_format={"type": "json_object"}
#                 )
#                 classification = json.loads(completion.choices[0].message.content)

#                 if classification.get("type") == "genuine":
#                     print(" -> Status: GENUINE QUESTION. Retrieving context...")
#                     retrieved_context = retrieve_context(sentence)

#                     answer_prompt = f"""Answer the question using ONLY the provided context. Format your entire answer as concise jot notes using bullet points. If the answer isn't in the context, say so concisely.

# Context:
# {retrieved_context}

# Question: {sentence}
# Answer (in jot notes):"""

#                     ans_completion = client.chat.completions.create(
#                         model="gpt-4o-mini",
#                         messages=[{"role": "user", "content": answer_prompt}]
#                     )
#                     answer = ans_completion.choices[0].message.content
#                     print(f" -> Answer:\n{answer}")
#                     results.append({"question": sentence, "type": "genuine", "answer": answer})
#                 else:
#                     print(" -> Status: Rhetorical / Skipped.")
#             except Exception as e:
#                 print(f"Error processing question: {e}")

#     return results

# if __name__ == "__main__":
#     default_file = "note.txt"
#     if os.path.exists(default_file):
#         with open(default_file, "r", encoding="utf-8") as f:
#             content = f.read()
#         qa_results = scan_and_answer_file(content)
#         print(f"\nScan complete! Answered {len([r for r in qa_results if r['type'] == 'genuine'])} genuine questions.")
#     else:
#         print(f"'{default_file}' not found.")