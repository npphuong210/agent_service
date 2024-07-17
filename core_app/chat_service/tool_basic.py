from langchain_community.tools import WikipediaQueryRun, tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
from core_app.models import Lecture, Conversation
import psycopg2
import os

import logging

logger = logging.getLogger(__name__)
class QueryInput(BaseModel):
    subject: str = Field(description="subject to look up on table database")
    chapter: str = Field(description="chapter to look up on table database")

@tool("query_data_from_db_table", args_schema=QueryInput)
def query_data_from_db_table(conversation: Conversation, subject: str, chapter: str) -> str:
    """Lấy dữ liệu từ bảng database."""
    logger.info(f"Received subject: {subject}, chapter: {chapter}")

    # Check if data is cached in knowledge field of Conversation
    if subject in conversation.knowledge and chapter in conversation.knowledge[subject]:
        logger.info("Data found in knowledge cache")
        return conversation.knowledge[subject][chapter]

    # Query data from database if not cached
    instance_qs = Lecture.objects.filter(subject=subject, chapter=chapter)
    if not instance_qs.exists():
        logger.warning("Data not found in database")
        return "Not Found"
    else:
        instance = instance_qs.first()
        content = instance.content

        # Update knowledge cache in Conversation model
        if subject not in conversation.knowledge:
            conversation.knowledge[subject] = {}
        conversation.knowledge[subject][chapter] = content
        conversation.save()
        
        logger.info("Data fetched from database and saved to knowledge cache")
        return content

tools = [query_data_from_db_table]