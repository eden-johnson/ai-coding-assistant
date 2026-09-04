import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "openai/gpt-oss-120b"


def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    chunks: [{"content", "file", "start_line", "end_line", "distance"}, ...]
    returns: answer string, grounded in the given chunks
    """
    context = "\n\n".join(
        f"# {c['file']} (lines {c['start_line']}-{c['end_line']})\n{c['content']}"
        for c in chunks
    )

    prompt = f"""You are a codebase assistant. Answer the question using ONLY the code below.
Cite the file path and line numbers in your answer. If the answer isn't in the code, say so.

Code:
{context}

Question: {question}
"""

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content