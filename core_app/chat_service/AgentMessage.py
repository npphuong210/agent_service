from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor, AgentType, initialize_agent
from langchain_core.messages import HumanMessage, AIMessage
from core_app.models import Conversation, SystemPrompt, ExternalKnowledge
from ca_vntl_helper import error_tracking_decorator
from langchain_community.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from core_app.models import ExternalKnowledge, Conversation
from ca_vntl_helper import error_tracking_decorator
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from core_app.models import Conversation, SystemPrompt
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from core_app.chat_service.AgentCreator import run_chatbot

def load_llm_model(provider="google"):
    if provider == "google":
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

    elif provider == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    else:
        raise Exception("Provider not supported")
    return llm

def convert_chat_dict_to_prompt(dict_message):
    if isinstance(dict_message, dict) and 'message_type' in dict_message and 'content' in dict_message:
        if dict_message['message_type'] == 'human_message':
            return HumanMessage(dict_message['content'])
        elif dict_message['message_type'] == 'ai_message':
            if dict_message['content'] == None:
                return AIMessage("")
            return AIMessage(dict_message['content'])
    return dict_message

@error_tracking_decorator
def get_message_from_agent(conversation_id, user_message):
    
    conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    
    conversation_instance = conversation_instance_qs.first()
    
    role = conversation_instance.agent.agent_name
    
    llm = conversation_instance.agent.llm
    
    prompt_content = conversation_instance.agent.prompt.prompt_content
    
    user_tools = conversation_instance.agent.tools
 
    chat_history_dicts = conversation_instance.chat_history or []
    
    if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
        chat_history_dicts.pop(0)
    
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]

    # Chạy agent
    print("run_chatbot")
    response = run_chatbot(
        user_message, chat_history, agent_role=role, llm_type=llm, prompt_content=prompt_content, user_tools=user_tools)
        
    print(response, "response")
    # Cập nhật lịch sử trò chuyện
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": response})

    # Lưu đối tượng Conversation
    conversation_instance.save()
        
    return response


# def get_streaming_response(conversation_id, user_message):
#     # Lấy đối tượng Conversation
#     conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
#     if not conversation_instance_qs.exists():
#         raise Exception("Conversation id not found")
#     conversation_instance = conversation_instance_qs.first()
#     character = conversation_instance.character_id
#     provider = conversation_instance.gpt_model
    
#     # Lấy lịch sử trò chuyện
#     chat_history_dicts = conversation_instance.chat_history or []

    
#     if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
#         chat_history_dicts.pop(0)

#     chat_history = [
#         convert_chat_dict_to_prompt(chat_history_dict)
#         for chat_history_dict in chat_history_dicts
#     ]

#     system_prompt_qs = SystemPrompt.objects.filter(character=character)
#     if not system_prompt_qs.exists():
#         raise Exception("Character not found")
    
#     system_prompt_instance = system_prompt_qs.first()
#     system_prompt = system_prompt_instance.prompt

#     lecture_qs = ExternalKnowledge.objects.all()
#     subject = lecture_qs.values_list('subject', flat=True)
#     chapter = lecture_qs.values_list('chapter', flat=True)
    
#     # system prompt content
#     sub_prompt = """Bạn có thể lấy thông tin được lưu trong 'InternalKnowledge' để trả lời,
#     nếu 'InternalKnowledge' rỗng hoặc thông tin trong 'InternalKnowledge' không phù hợp để trả lời thì hãy sử dụng chức năng công cụ 'query_data_from_db_table' để lấy thông tin từ cơ sở dữ liệu với đầu vào: subject, chapter'
#     InternalKnowledge: 
#     """
#     @tool("query_data_from_db_table", args_schema=QueryInput)
    
#     def query_data_from_db_table(subject: str, chapter: str) -> str:
#         """Get data from database table."""
#         instance_qs = ExternalKnowledge.objects.filter(subject=subject, chapter=chapter)
#         if not instance_qs.exists():
#             return "Not Found"
#         else:
#             instance = instance_qs.first()
#             # conversation_instance.InternalKnowledge = instance.content  # Save changes to the database
#             # conversation_instance.save()
#             return instance.content
            
#     tools = [query_data_from_db_table]

#     system_prompt_content = f"""{system_prompt} 
#                            Bạn sẽ truy cập danh sách được gợi ý sau: với {subject}, {chapter}\n
#                            Bạn sẽ hiểu nội dung câu hỏi và đưa ra subject và chapter chính xác hoặc gần đúng nhất trong database. \n
#                            {sub_prompt}
#                            """
#     # create system prompt
#     system_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system",system_prompt_content),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{input}"),
#             MessagesPlaceholder(variable_name="agent_scratchpad"),
#         ]
#     )
#     # load llm model

#     llm = load_llm_model(provider)

#     agent = create_tool_calling_agent(llm, tools, system_prompt)
#     agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_results=False)

#     return agent_executor, chat_history, conversation_instance


    