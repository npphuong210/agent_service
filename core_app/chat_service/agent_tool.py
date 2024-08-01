from core_app.models import InternalKnowledge, ExternalKnowledge
from langchain_community.tools import WikipediaQueryRun, tool, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
import requests
from pgvector.django import L2Distance
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
from django.db import connection

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
            distance=L2Distance("hashtags_embedding", embedded)
        ).order_by("distance")[:1]
        
        # Check if similar hashtags were found
        if not internal_knowledge_qs:
            # query_embedding = get_vector_from_embedding(query)
            internal_knowledge_qs = InternalKnowledge.objects.annotate(
                distance=L2Distance("summary_embedding", embedded)
            ).order_by("distance")[:1]
            summaries = [internal_knowledge.summary for internal_knowledge in internal_knowledge_qs]
            summary_output = "Similar hashtags found:\n" + "\n".join(summaries)
            return summary_output
            
        # Generate a summary of the matching entries
        summaries = [internal_knowledge.summary for internal_knowledge in internal_knowledge_qs]
        summary_output = "Similar hashtags found:\n" + "\n".join(summaries)
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
        #print(instance.content)
        return instance.content
    
def hybrid_search_for_internal(query_text, query_vector, k=60):

    sql = """
    WITH semantic_search AS (
        SELECT id, RANK () OVER (ORDER BY summary_embedding <=> %(query_vector)s::vector) AS rank
        FROM core_app_internalknowledge
        ORDER BY summary_embedding <=> %(query_vector)s::vector
        LIMIT 20
    ),
    keyword_search AS (
        SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', summary), query) DESC), summary
        FROM core_app_internalknowledge, plainto_tsquery('english', %(query_text)s) query
        WHERE to_tsvector('english', summary) @@ query
        ORDER BY ts_rank_cd(to_tsvector('english', summary), query) DESC
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
        cursor.execute(sql, {'query_text': query_text, 'query_vector': query_vector, 'k': k})
        results = cursor.fetchall()
    return results
  
class HybridSreachInput(BaseModel):
    query_text: str = Field(description="user's query to search ")
    
@tool("hybrid_search_db", args_schema=HybridSreachInput)
def hybrid_search_db(query_text: str) -> str:
    """use user query and embedding query to search"""
    embedding_query = get_vector_from_embedding(query_text)
    result = hybrid_search_for_internal(query_text, embedding_query)
    return result[0][1]
    
 

tool_mapping = {
    "query_data_from_wikipedia": query_data_from_wikipedia,
    "search_data_from_duckduckgo": search_data_from_duckduckgo,
    "request_data_from_furl": request_data_from_url,
    "query_internal_knowledge": query_internal_knowledge,
    "query_external_knowledge": query_external_knowledge,
    "hybrid_search_db": hybrid_search_db,
    
}


# output = hybrid_search_for_external("khổ đầu tiên trong thờ vùng mỏ", get_vector_from_embedding("khổ đầu tiên trong thơ vùng mỏ"))

# for row in output:
#     print('document:', row[1], 'RRF score:', row[2])
#     print(row)