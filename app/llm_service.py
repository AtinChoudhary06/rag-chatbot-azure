from openai import OpenAI
import os

def get_chat_client():
    return OpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY")
    )

def generate_answer(question: str, context_chunks: list[str], history: list[dict]) -> str:
    client = get_chat_client()
    context = "\n\n---\n\n".join(context_chunks)
    system = f"""You are a helpful document assistant.
Answer only from the context below. If the answer is not in the context, say so clearly.
CONTEXT:
{context}"""
    messages = [{"role": "system", "content": system}] + history[-6:] + [{"role": "user", "content": question}]
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=messages,
        temperature=0.3,
        max_tokens=1000
    )
    return response.choices[0].message.content