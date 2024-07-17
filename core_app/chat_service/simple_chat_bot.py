import os

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from core_app.models import Conversation, SystemPrompt

def convert_dict_to_template_message(dict_message):
    print(dict_message)
    if dict_message["message_type"] == "human_message":
        return HumanMessage(dict_message["content"])
    elif dict_message["message_type"] == "ai_message":
        return AIMessage(dict_message["content"])
    else:
        raise Exception("Message type not supported")

def load_llm_model(provider="google"):
    if provider == "google":
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

    elif provider == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    else:
        raise Exception("Provider not supported")
    return llm

def select_system_prompt(character="healthy-care"):
    # load model instance qs by filfer
    system_prompt_qs = SystemPrompt.objects.filter(character=character)
    if not system_prompt_qs.exists():
        raise Exception("Character not found")
    system_prompt_instance = system_prompt_qs.first()
    system_prompt = system_prompt_instance.prompt

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}"),
    ])
    return prompt

def run_chatbot(input_text, chat_history, character="healthy-care", provider="google"):
    # load llm
    print("here")
    llm = load_llm_model(provider)
    print(llm)
    # select prompt and character
    prompt = select_system_prompt(character)
    # init chain
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": input_text, "chat_history": chat_history})
    ## load from agent executor
    return output

def get_message_from_chatbot(conversation_id, user_message):
    # user_input = user_message
    # chat_history
    # character
    # provider
    # ==> conversation_model

    conversation_instance_qs = Conversation.objects.filter(id=conversation_id) # list
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    conversation_instance = conversation_instance_qs.first()

    character = conversation_instance.prompt_name
    provider = conversation_instance.gpt_model
    chat_history_dicts = conversation_instance.chat_history
    
    if not chat_history_dicts:
        print('chat_history is empty')
        chat_history = []
    else:
        chat_history = [convert_dict_to_template_message(chat_history_dict) for chat_history_dict in chat_history_dicts]
    #chat_history = [convert_dict_to_template_message(chat_history_dict) for chat_history_dict in chat_history_dicts]

    response = run_chatbot(user_message, chat_history, character=character, provider=provider)
    # chat_history.append(HumanMessage(user_input))
    # chat_history.append(AIMessage(response))
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": response})

    conversation_instance.save()

    return response

