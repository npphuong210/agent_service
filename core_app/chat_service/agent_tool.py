from core_app.models import InternalKnowledge, ExternalKnowledge, Conversation
from langchain_community.tools import WikipediaQueryRun, tool, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
import requests
from pgvector.django import L2Distance
from core_app.embedding.embedding_by_openai import get_vector_from_embedding

duckduckgosearch = DuckDuckGoSearchRun()

class DuckDuckGoSearchInput(BaseModel):
    query: str = Field(description="query to search on duckduckgo")
    
@tool("search_data_from_duckduckgo", args_schema=DuckDuckGoSearchInput)
def search_data_from_duckduckgo(query: str) -> str:
    """Search data from duckduckgo."""
    output = duckduckgosearch.run(query)
    return output

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
    # hashtags: str = Field(description="Hashtags to find similar hashtags")
    query: str = Field(description="use this query to find similar summaries")

@tool("query_internal_knowledge", args_schema=HashTagInput)
def query_internal_knowledge(query: str) -> str:
    """Find similar a summary information by a query string"""
    try:
        embedded = get_vector_from_embedding(query)
        internal_knowledge_qs = InternalKnowledge.objects.annotate(
            distance=L2Distance("summary_embedding", embedded)
        ).order_by("distance")[:1]
        
        summaries = [internal_knowledge.summary for internal_knowledge in internal_knowledge_qs]
        summary_output = "Similar summary found:\n" + "\n".join(summaries)
        return summary_output
    
    except Exception as e:
        return f"An error occurred: {e}"
    
class QueryDatabase(BaseModel):
    subject: str = Field(description="subject to look up on table database")
    chapter: str = Field(description="chapter to look up on table database")
 
@tool("query_external_knowledge", args_schema=QueryDatabase)
def query_external_knowledge(subject: str, chapter: str) -> str:
    """Get data from external knowledge table."""
    instance_qs = ExternalKnowledge.objects.filter(subject=subject, chapter=chapter)
    
    if not instance_qs.exists():
        return "Not Found"
    else:
        instance = instance_qs.first()
        return instance.content
class TraceBackInput(BaseModel):
    query: str = Field(description="use this query to find similar user question")


@tool("trace_back", args_schema=TraceBackInput)
def trace_back(query: str) -> str:
    """Trace back the last question and the answer."""
    conversation_instance_qs = Conversation.objects.all().order_by("-updated_at")
    if not conversation_instance_qs.exists():
        return "No conversation found"
    else:
        conversation_instance = conversation_instance_qs[1]
        chat_history = conversation_instance.chat_history
        if not chat_history:
            return "No chat history found"
        last_dict = chat_history[-2:]

        output = f"""The last question asked was:
                    human_message: {last_dict[0]['content']}
                    agent_message: {last_dict[1]['content']}
                    """       
    return output


tool_mapping = {
    "query_data_from_wikipedia": query_data_from_wikipedia,
    "search_data_from_duckduckgo": search_data_from_duckduckgo,
    "request_data_from_url": request_data_from_url,
    "query_internal_knowledge": query_internal_knowledge,
    "query_external_knowledge": query_external_knowledge,
    "trace_back": trace_back
}


