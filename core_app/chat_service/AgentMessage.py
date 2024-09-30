from ca_vntl_helper import error_tracking_decorator
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from core_app.models import Conversation, InternalKnowledge
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from core_app.chat_service.AgentCreator import run_chatbot, AgentCreator
from core_app.extract import extract
from core_app.embedding.graph_embedding import graph_embedding
import os

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
            if dict_message['content'] == None:
                return HumanMessage("")
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
    llm_id = conversation_instance.agent.llm_id
    prompt_content = conversation_instance.agent.prompt.prompt_content
    user_tools = conversation_instance.agent.tools
    user = conversation_instance.agent.user.id
    agent = conversation_instance.agent.id
    is_use_internal_knowledge = conversation_instance.is_use_internal_knowledge
    chat_history_dicts = conversation_instance.chat_history or []
    
    if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
        chat_history_dicts.pop(0)
    
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]

    output_message = run_chatbot(
        user_message, chat_history, agent_role=role, llm_id=llm_id, prompt_content=prompt_content, user_tools=user_tools, user=user, agent=agent, is_use_internal_knowledge=is_use_internal_knowledge)
    
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": output_message})
    conversation_instance.save()
    #graph_embedding(user, user_message, output_message)
    response = {
        "ai_message": output_message,
        "human_message": user_message,
    }
    return response

def get_streaming_agent_instance(conversation_id):

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

    agent_instance = AgentCreator(agent_name=role, llm_type=llm, prompt_content=prompt_content, tools=user_tools)
    return agent_instance.create_agent_executor(), chat_history, conversation_instance


    