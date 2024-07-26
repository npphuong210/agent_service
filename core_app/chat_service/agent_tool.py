from core_app.models import InternalKnowledge
from langchain_community.tools import WikipediaQueryRun, tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
import requests
from pgvector.django import L2Distance
from core_app.embedding.embedding_by_openai import get_vector_from_embedding

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

class QueryInput(BaseModel):
    query: str = Field(description="query to look up on wikipedia")


@tool("query_data_from_wikipedia", args_schema=QueryInput)
def query_data_from_wikipedia(query: str) -> str:
    """Get data from wikipedia."""
    output = WikipediaAPIWrapper().run(query)
    return output


class RequestInput(BaseModel):
    url: str = Field(description="URL to request from")
    type: str = Field(description="GET or POST")


@tool("request_data_from_url", args_schema=RequestInput)
def request_data_from_url(url: str, type: str) -> str:
    """Request data from a URL."""
    try:
        if type.upper() == "GET":
            response = requests.get(url)
        elif type.upper() == "POST":
            response = requests.post(url)
        else:
            return f"Invalid request type: {type}. Use 'GET' or 'POST'."

        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.RequestException as e:
        return f"An error occurred: {e}"


class HashTagInput(BaseModel):
    hashtags: str = Field(description="Hashtags to find similar hashtags")


@tool("query_internal_knowledge", args_schema=HashTagInput)
def query_internal_knowledge(hashtags: str) -> str:
    """Find similar hashtags and return a summary"""
    try:
        hashtags_embedding = get_vector_from_embedding(hashtags)
        internal_knowledge_qs = InternalKnowledge.objects.annotate(
            distance=L2Distance("hashtags_embedding", hashtags_embedding)
        ).order_by("distance")[:1]

        # Check if similar hashtags were found
        if not internal_knowledge_qs:
            return "No similar hashtags found."

        # Generate a summary of the matching entries
        summaries = [internal_knowledge.summary for internal_knowledge in internal_knowledge_qs]
        summary_output = "Similar hashtags found:\n" + "\n".join(summaries)

        print(summary_output)

        return summary_output
    except Exception as e:
        return f"An error occurred: {e}"

tool_mapping = {
    "query_data_from_wikipedia": query_data_from_wikipedia,
    "request_data_from_url": request_data_from_url,
    "query_internal_knowledge": query_internal_knowledge
}
