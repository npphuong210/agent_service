import re
from core_app.embedding.embedding_by_openai import get_vector_from_embedding


import re

def extract(ai_response: str, user_message: str) -> dict:
    # Initialize variables
    summary = ""
    ai_hashtags = []
    combined_hashtags = []
    cut_message = ""

    if ai_response:
        # Extract summary from AI response
        summary_pattern = re.compile(r'Summary:\s*(.*?)\s*Hashtag:', re.DOTALL)
        summary_match = summary_pattern.search(ai_response)
        if summary_match:
            summary = summary_match.group(1).strip()

        # Extract hashtags from AI response
        hashtags_pattern = re.compile(r'Hashtag:\s*(.*?)$', re.DOTALL)
        hashtags_match = hashtags_pattern.search(ai_response)
        if hashtags_match:
            ai_hashtags = [f"#{tag.strip()}" for tag in hashtags_match.group(1).strip().split('#') if tag.strip()]

        # Extract message_output
        cut_message = ai_response.split("Summary:")[0]
        if " Actual Output:" in cut_message:
            cut_message = cut_message.split(" Actual Output:")[-1].strip()

    if user_message:
        # Extract hashtags from the user message
        user_hashtags = [f"#{tag.strip()}" for tag in re.findall(r"#(\w+)", user_message)]
        # Combine AI hashtags and user hashtags
        combined_hashtags = list(set(ai_hashtags + user_hashtags))
    else:
        combined_hashtags = ai_hashtags

    # Convert combined hashtags to a comma-separated string
    combined_hashtags_str = ', '.join(combined_hashtags)

    # Compute embeddings
    summary_embedding = get_vector_from_embedding(summary)
    hashtags_embedding = get_vector_from_embedding(combined_hashtags_str)

    return {
        'summary': summary,
        'hashtags': combined_hashtags,
        'message_output': cut_message,
        'summary_embedding': summary_embedding,
        'hashtags_embedding': hashtags_embedding
    }

# temp1 = extract("Hello! How can I assist you today?", "hello")
# temp1 = extract("- Actual Output: May 1 is the 121st day of the year (122nd in leap years) in the Gregorian calendar; 244 days remain until the end of the year. - Summary: May 1 marks the 121st day of the year in the Gregorian calendar. - Hashtag: #May1 #GregorianCalendar #CalendarFacts", "ello")
# print(f"""summary: {temp1['summary']} \n hashtags: {temp1['hashtags']} \n message_output: {temp1['message_output']}""")