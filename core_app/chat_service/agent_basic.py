from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor, AgentType, initialize_agent
from langchain_core.messages import HumanMessage, AIMessage
from core_app.chat_service.simple_chat_bot import load_llm_model

from core_app.models import Conversation, SystemPrompt, Lecture
from ca_vntl_helper import error_tracking_decorator
import json
import logging
logger = logging.getLogger(__name__)

from langchain_community.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from core_app.models import Lecture, Conversation
from ca_vntl_helper import error_tracking_decorator
import psycopg2
import os
from django.db import transaction

#streaming 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

class QueryInput(BaseModel):
    subject: str = Field(description="subject to look up on table database")
    chapter: str = Field(description="chapter to look up on table database")
    


def convert_chat_dict_to_prompt(dict_message):
    if isinstance(dict_message, dict) and 'message_type' in dict_message and 'content' in dict_message:
        if dict_message['message_type'] == 'human_message':
            return HumanMessage(dict_message['content'])
        elif dict_message['message_type'] == 'ai_message':
            return AIMessage(dict_message['content'])
    return dict_message

def run_lecture_agent(input, chat_history, character, provider, knowledge, conversation_instance):
    # prompt search information from wikipedia (tools)
    
    system_prompt_qs = SystemPrompt.objects.filter(character=character)
    if not system_prompt_qs.exists():
        raise Exception("Character not found")
    
    # conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    # if not conversation_instance_qs.exists():
        # raise Exception("Conversation id not found")
    # conversation_instance = conversation_instance_qs.first()

    # knowledge = conversation_instance.knowledge
    
    
    # get system prompt
    system_prompt_instance = system_prompt_qs.first()
    system_prompt = system_prompt_instance.prompt

    lecture_qs = Lecture.objects.all()
    subject = lecture_qs.values_list('subject', flat=True)
    chapter = lecture_qs.values_list('chapter', flat=True)
    
    # system prompt content
    sub_prompt = """Bạn có thể lấy thông tin được lưu trong 'knowledge' để trả lời,
    nếu 'knowledge' rỗng hoặc thông tin trong 'knowledge' không phù hợp để trả lời thì hãy sử dụng chức năng công cụ 'query_data_from_db_table' để lấy thông tin từ cơ sở dữ liệu với đầu vào: subject, chapter'
    knowledge: {knowledge}
    """
    @tool("query_data_from_db_table", args_schema=QueryInput)
    
    def query_data_from_db_table(subject: str, chapter: str) -> str:
        """Get data from database table."""
        instance_qs = Lecture.objects.filter(subject=subject, chapter=chapter)
        if not instance_qs.exists():
            return "Not Found"
        else:
            instance = instance_qs.first()
            
            
            conversation_instance.knowledge = instance.content  # Save changes to the database
            conversation_instance.save()
            return instance.content
            
    tools = [query_data_from_db_table]

    system_prompt_content = f"""{system_prompt} 
                           Bạn sẽ truy cập danh sách được gợi ý sau: với conversation {conversation_instance.id} {subject}, {chapter}\n
                           Bạn sẽ hiểu nội dung câu hỏi và đưa ra subject và chapter chính xác hoặc gần đúng nhất trong database. \n
                           {sub_prompt}
                           """
    print(system_prompt_content)
    # create system prompt
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",system_prompt_content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    # load llm model

    llm = load_llm_model(provider)

    # create agent constructor
    agent = create_tool_calling_agent(llm, tools, system_prompt)
    # create agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    # invoke agent
    output = agent_executor.invoke({
            "input": input,
            "chat_history": chat_history,
            'knowledge': knowledge,
            
        })
    
    conversation_instance.save()
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    updated_knowledge = output.get('knowledge', knowledge)
    print(updated_knowledge)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    return output['output']

    
@error_tracking_decorator
def get_message_from_agent(conversation_id, user_message):
    # Lấy đối tượng Conversation
    conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    conversation_instance = conversation_instance_qs.first()
    character = conversation_instance.prompt_name
    provider = conversation_instance.gpt_model
    knowledge = conversation_instance.knowledge
 
    # Lấy lịch sử trò chuyện
    chat_history_dicts = conversation_instance.chat_history or []
    
    if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
        chat_history_dicts.pop(0)
    
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]

    # Chạy agent
    response = run_lecture_agent(
        user_message, chat_history, character=character, provider=provider, knowledge=knowledge, conversation_instance = conversation_instance
    )
        
    # Cập nhật lịch sử trò chuyện
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": response})

    # Lưu đối tượng Conversation
    try:
        conversation_instance.save()
        print("Conversation instance saved successfully.")
    except Exception as e:
        print(f"Failed to save chat history: {e}")
        
    return response


def get_streaming_response(conversation_id, user_message):
    # Lấy đối tượng Conversation
    conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    conversation_instance = conversation_instance_qs.first()
    character = conversation_instance.character_id
    provider = conversation_instance.gpt_model
    
    # Lấy lịch sử trò chuyện
    chat_history_dicts = conversation_instance.chat_history or []
    print(chat_history_dicts)
    print("---------------------------------")
    
    if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
        chat_history_dicts.pop(0)
    print(chat_history_dicts)
    print("---------------------------------")
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]
    print(chat_history)

    system_prompt_qs = SystemPrompt.objects.filter(character=character)
    if not system_prompt_qs.exists():
        raise Exception("Character not found")
    
    system_prompt_instance = system_prompt_qs.first()
    system_prompt = system_prompt_instance.prompt

    lecture_qs = Lecture.objects.all()
    subject = lecture_qs.values_list('subject', flat=True)
    chapter = lecture_qs.values_list('chapter', flat=True)
    
    # system prompt content
    sub_prompt = """Bạn có thể lấy thông tin được lưu trong 'knowledge' để trả lời,
    nếu 'knowledge' rỗng hoặc thông tin trong 'knowledge' không phù hợp để trả lời thì hãy sử dụng chức năng công cụ 'query_data_from_db_table' để lấy thông tin từ cơ sở dữ liệu với đầu vào: subject, chapter'
    knowledge: {knowledge}
    """
    @tool("query_data_from_db_table", args_schema=QueryInput)
    
    def query_data_from_db_table(subject: str, chapter: str) -> str:
        """Get data from database table."""
        instance_qs = Lecture.objects.filter(subject=subject, chapter=chapter)
        if not instance_qs.exists():
            return "Not Found"
        else:
            instance = instance_qs.first()
            # conversation_instance.knowledge = instance.content  # Save changes to the database
            # conversation_instance.save()
            return instance.content
            
    tools = [query_data_from_db_table]

    system_prompt_content = f"""{system_prompt} 
                           Bạn sẽ truy cập danh sách được gợi ý sau: với {subject}, {chapter}\n
                           Bạn sẽ hiểu nội dung câu hỏi và đưa ra subject và chapter chính xác hoặc gần đúng nhất trong database. \n
                           {sub_prompt}
                           """
    # create system prompt
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",system_prompt_content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    # load llm model

    llm = load_llm_model(provider)

    # create agent constructor
    agent = initialize_agent(
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        verbose=True,
        return_intermediate_results=False
    )
    
    output = agent.invoke({
        "input": user_message,
        "chat_history": chat_history
        })
        
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": output['output']})
    conversation_instance.save()
    return output


    