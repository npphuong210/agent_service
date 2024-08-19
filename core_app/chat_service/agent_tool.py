from core_app.models import InternalKnowledge, ExternalKnowledge, Conversation

from langchain_community.tools import WikipediaQueryRun, tool, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
import requests
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
from django.db import connection
from pgvector.django import L2Distance
from langchain.agents import Tool


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

class SummaryInput(BaseModel):
    query: str = Field(description="use this query to find similar summaries")
    user: str = Field(description="user name")
    agent: str = Field(description="agent name")

@tool("query_internal_knowledge", args_schema=SummaryInput)
def query_internal_knowledge(query: str, user: str, agent: str) -> str:
    """Find similar a summary information by a query string"""
    try:
        embedded = get_vector_from_embedding(query)
        internal_knowledge_qs = InternalKnowledge.objects.filter(user=user,agent=agent).annotate(
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

def hybrid_search_for_internal(query_text, query_vector, language, k=20):

    sql = """
    WITH semantic_search AS (
        SELECT id, RANK () OVER (ORDER BY summary_embedding <=> %(query_vector)s::vector) AS rank
        FROM core_app_internalknowledge
        ORDER BY summary_embedding <=> %(query_vector)s::vector
        LIMIT 20
    ),
    keyword_search AS (
        SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector(%(language)s, summary), query) DESC), summary
        FROM core_app_internalknowledge, plainto_tsquery(%(language)s, %(query_text)s) query
        WHERE to_tsvector(%(language)s, summary) @@ query
        ORDER BY ts_rank_cd(to_tsvector(%(language)s, summary), query) DESC
        LIMIT 20
    )
        
    SELECT
      COALESCE(semantic_search.id, keyword_search.id) AS id,    
      summary,
      COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
      COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
    FROM semantic_search
    FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
    ORDER BY score DESC
    LIMIT 5
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, {'query_text': query_text, 'query_vector': query_vector, "language" : language,'k': k})
        results = cursor.fetchall()
    return results
  
class HybridSreachInput(BaseModel):
    query_text: str = Field(description="user's query to search ")
    language: str = Field(description="language to search")
    
@tool("hybrid_search_internal_db", args_schema=HybridSreachInput)
def hybrid_search_internal_db(query_text: str, language: str) -> str:
    """use user query and embedding query to search"""
    embedding_query = get_vector_from_embedding(query_text)
    result = hybrid_search_for_internal(query_text, embedding_query, language)
    full_text = ""
    for content in result:
        full_text += str(content[1]) + "\n"
    return full_text


def hybrid_search_for_external(query_text, query_vector, language, k=20):

    sql = """
    WITH semantic_search AS (
        SELECT id, RANK () OVER (ORDER BY content_embedding <=> %(query_vector)s::vector) AS rank
        FROM core_app_externalknowledge
        ORDER BY content_embedding <=> %(query_vector)s::vector
        LIMIT 20
    ),
    keyword_search AS (
        SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC), content
        FROM core_app_externalknowledge, plainto_tsquery(%(language)s, %(query_text)s) query
        WHERE to_tsvector(%(language)s, content) @@ query
        ORDER BY ts_rank_cd(to_tsvector(%(language)s, content), query) DESC
        LIMIT 20
    )
        
    SELECT
      COALESCE(semantic_search.id, keyword_search.id) AS id,    
      content,
      COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
      COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
    FROM semantic_search
    FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
    ORDER BY score DESC
    LIMIT 5
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, {'query_text': query_text, 'query_vector': query_vector, "language": language , 'k': k})
        results = cursor.fetchall()
    return results


@tool("hybrid_search_external_db", args_schema=HybridSreachInput)
def hybrid_search_external_db(query_text: str, language: str):
    """user query to search"""
    embedded = get_vector_from_embedding(query_text)
    knowledge_qs = ExternalKnowledge.objects.annotate(
        distance=L2Distance("content_embedding", embedded)
        ).order_by("distance")[:3]
    results = [(knowledge.content, rank) for rank, knowledge in enumerate(knowledge_qs)]
    return results
# def hybrid_search_external_db(query_text: str, language: str) -> str:
#     """use user query and embedding query to search"""
#     embedding_query = get_vector_from_embedding(query_text)
#     result = hybrid_search_for_external(query_text, embedding_query, language)
#     full_text = ""
#     for content in result:
#         full_text += str(content[1]) + "\n"
#     return full_text


class NoOpInput(BaseModel):
    info: str = Field(description="Information to process")

@tool("noop_tool", args_schema=NoOpInput)
def noop_tool(info: str) -> str:
    """just return the intact info"""
    return info

class ContentInput(BaseModel):
    query: str = Field(description="use this query to find similar contents")

@tool("external_content_search", args_schema=ContentInput)
def external_content_search(query: str) -> str:
    """Find similar a content information by a query string"""
    try:
        embedded = get_vector_from_embedding(query)
        external_knowledge_qs = ExternalKnowledge.objects.annotate(
            distance=L2Distance("content_embedding", embedded)
        ).order_by("distance")[:1]
        
        summaries = [internal_knowledge.summary for internal_knowledge in external_knowledge_qs]
        summary_output = "Similar summary found:\n" + "\n".join(summaries)
        return summary_output
    
    except Exception as e:
        return f"An error occurred: {e}"



tool_mapping = {
    "query_data_from_wikipedia": query_data_from_wikipedia,
    "search_data_from_duckduckgo": search_data_from_duckduckgo,
    "request_data_from_url": request_data_from_url,
    "query_internal_knowledge": query_internal_knowledge,
    "query_external_knowledge": query_external_knowledge,
    "hybrid_search_internal_db": hybrid_search_internal_db,
    "hybrid_search_external_db": hybrid_search_external_db,
    "noop_tool": noop_tool,
    
}