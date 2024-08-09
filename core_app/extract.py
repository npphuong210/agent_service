import re
from core_app.embedding.embedding_by_openai import get_vector_from_embedding


import re

def extract(ai_response: str, user_message: str) -> dict:
    # Initialize variables
    summary = ""
    # Extract summary from AI response
    summary_pattern = re.compile(r'Summary:\s*(.*)', re.DOTALL)
    summary_match = summary_pattern.search(ai_response)
    if summary_match:
        summary = summary_match.group(1).strip()
    summary_embedding = get_vector_from_embedding(summary)


    return {
        'summary': summary,
        'summary_embedding': summary_embedding,
    }