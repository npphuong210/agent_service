from langchain_community.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from core_app.models import Lecture, Conversation
from ca_vntl_helper import error_tracking_decorator
import psycopg2
import os

class QueryInput(BaseModel):
    subject: str = Field(description="subject to look up on table database")
    chapter: str = Field(description="chapter to look up on table database")
    
@tool("query_data_from_db_table", args_schema=QueryInput)
def query_data_from_db_table(subject: str, chapter: str) -> str:
    """Get data from database table."""
    instance_qs = Lecture.objects.filter(subject=subject, chapter=chapter)
    if not instance_qs.exists():
        return "Not Found"
    else:
        instance = instance_qs.first()
        print(instance.content)
        return instance.content
        
tools = [query_data_from_db_table]