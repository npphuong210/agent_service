from core_app.models import InternalKnowledge, ExternalKnowledge, Conversation
from langchain_community.tools import WikipediaQueryRun, tool, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from pydantic import BaseModel, Field
import requests
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
from django.db import connection
from pgvector.django import L2Distance
from langchain.agents import Tool
from core_app.external.external_tool import create_multi_queries, vector_search, reciprocal_rank_fusion, retrieve_documents_with_rrf
import logging

logger = logging.getLogger(__name__)

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
    user: int = Field(description="user id")
    agent: str = Field(description="agent id")

@tool("query_internal_knowledge", args_schema=SummaryInput)
def query_internal_knowledge(query: str, user: int, agent: str) -> str:
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

class NoOpInput(BaseModel):
    info: str = Field(description="Information to process")

@tool("noop_tool", args_schema=NoOpInput)
def noop_tool(info: str) -> str:
    """just return the intact info"""
    return info

class ContentInput(BaseModel):
    query: str = Field(description="use this query to find similar contents")
    
@tool("external_content_search", args_schema=ContentInput)
def external_content_search(query: str, max_results: int = 3) -> str:
    """Find similar content information by a query string, with multiple results and better error handling."""
    try:
        # Generate the vector from the query string
        embedded = get_vector_from_embedding(query)
        
        # Annotate queryset with distances for multiple embeddings: content, subject, and chapter
        external_knowledge_qs = ExternalKnowledge.objects.annotate(
            content_distance=L2Distance("content_embedding", embedded),
            subject_distance=L2Distance("subject_embedding", embedded),
            chapter_distance=L2Distance("chapter_embedding", embedded)
        ).order_by("content_distance", "subject_distance", "chapter_distance")[:max_results]
        
        # If no results found, provide a message
        if not external_knowledge_qs.exists():
            return "No similar content found for your query."
        
        # Prepare summary of results with distances
        results = []
        for knowledge in external_knowledge_qs:
            summary = knowledge.content  # Limit to first 200 chars for summary
            results.append(
                f"Subject: {knowledge.subject}, Chapter: {knowledge.chapter}\n"
                f"Summary: {summary}...\n"
                f"Distance: {knowledge.content_distance:.2f} (Content), "
                f"{knowledge.subject_distance:.2f} (Subject), "
                f"{knowledge.chapter_distance:.2f} (Chapter)\n"
            )
        
        # Join the results into a single string output
        summary_output = f"{len(results)} Similar results found:\n" + "\n".join(results)
        return summary_output
    
    except Exception as e:
        # Log error message for debugging
        logger.error(f"Error during external content search: {e}")
        return f"An error occurred: {str(e)}"


class InputQuery(BaseModel):
    """ Input query to search """
    query: str = Field(description="The user query to search",)
    
@tool("multi_query", args_schema=InputQuery)
def multi_query(query: str) -> str:
    try:
        """based on the user query, create multiple queries to search"""
        similar_queries =  create_multi_queries(query)     
        similar_queries.append(f"\noriginal query. {query}")
        top_knowledge = retrieve_documents_with_rrf(similar_queries)
        context = "".join([content for content, _ in top_knowledge])       
        context = f"According to the knowledge base, {context}. \n question: {query}"    
        return context
    except Exception as e:
        return "Don't have any information"

# list of tool
tool_mapping = {
    "query_data_from_wikipedia": query_data_from_wikipedia,
    "search_data_from_duckduckgo": search_data_from_duckduckgo,
    "request_data_from_url": request_data_from_url,
    "query_internal_knowledge": query_internal_knowledge,
    "query_external_knowledge": query_external_knowledge,
    "noop_tool": noop_tool,
    "multi_query": multi_query,
    "external_content_search": external_content_search,
}