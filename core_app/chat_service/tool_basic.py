from langchain_community.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from core_app.models import Lecture, Conversation
from ca_vntl_helper import error_tracking_decorator
import psycopg2
import os

class QueryInput(BaseModel):
    conversation_id: int = Field(description="ID of the conversation to update")
    subject: str = Field(description="subject to look up on table database")
    chapter: str = Field(description="chapter to look up on table database")
    
@tool("query_data_from_db_table", args_schema=QueryInput)
def query_data_from_db_table(conversation_id: int, subject: str, chapter: str) -> str:
    """Get data from database table."""
    instance_qs = Lecture.objects.filter(subject=subject, chapter=chapter)
    if not instance_qs.exists():
        return "Not Found"
    else:
        conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
        if not conversation_instance_qs.exists():
            return 'Conversation not found'
        conversation_instance = conversation_instance_qs.first()
        instance = instance_qs.first()
        return instance.content
        
tools = [query_data_from_db_table]