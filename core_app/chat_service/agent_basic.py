from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from core_app.chat_service.simple_chat_bot import load_llm_model
from core_app.chat_service.tool_basic import tools, query_data_from_db_table
from core_app.models import Conversation, SystemPrompt, Lecture
from ca_vntl_helper import error_tracking_decorator
import json
import logging
logger = logging.getLogger(__name__)

def convert_chat_dict_to_prompt(dict_message):
    if isinstance(dict_message, dict) and 'message_type' in dict_message and 'content' in dict_message:
        if dict_message['message_type'] == 'human_message':
            return HumanMessage(dict_message['content'])
        elif dict_message['message_type'] == 'ai_message':
            return AIMessage(dict_message['content'])
    return dict_message

def run_lecture_agent(input, chat_history, character, provider, conversation_instance):
    # prompt search information from wikipedia (tools)
    
    system_prompt_qs = SystemPrompt.objects.filter(character=character)
    if not system_prompt_qs.exists():
        raise Exception("Character not found")
    
    # get system prompt
    system_prompt_instance = system_prompt_qs.first()
    system_prompt = system_prompt_instance.prompt
    print(conversation_instance)  
    # conversation_instance_qs = Conversation.objects.filter(id=conversation_instance)
    # conversation_instance_knowledge = conversation_instance_qs.first()
    knowledge = conversation_instance.knowledge
    print("###############", knowledge)

    lecture_qs = Lecture.objects.all()
    subject = lecture_qs.values_list('subject', flat=True)
    chapter = lecture_qs.values_list('chapter', flat=True)
    # system prompt content
    sub_prompt = ("Bạn có thể lấy thông tin bên dưới để trả lời,"
                  "{knowledge}"
                  "nếu thông tin bên trên rỗng hoặc thông tin bên trên không phù hợp để trả lời"
                  "thì hãy sử dụng chức năng công cụ 'query_data_from_db_table' "
                  "để lấy thông tin từ cơ sở dữ liệu với đầu vào: "
                  "'query_data_from_db_table('subject', 'chapter')'")
    system_prompt_content = (f"""{system_prompt} 
                           Bạn sẽ truy cập danh sách được gợi ý sau: với conversation {conversation_instance.id}, {subject}, {chapter}\n
                           Bạn sẽ hiểu nội dung câu hỏi và đưa ra subject và chapter chính xác hoặc gần đúng nhất trong database. \n
                           {sub_prompt}
                           """)
    # create system prompt
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",system_prompt_content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    print("######################################")
    print(system_prompt)
    # load llm model
    llm = load_llm_model(provider)

    # create agent constructor
    agent = create_tool_calling_agent(llm, tools, system_prompt)
    # create agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    # invoke agent
    try:
        output = agent_executor.invoke({
            "input": input, 
            "chat_history": chat_history, 
            'knowledge': knowledge or '',
            'conversation_id': conversation_instance.id
        })
    except Exception as e:
        print(e)
        return {'output': '', 'knowledge': knowledge}
    
    # knowledge_content = query_data_from_db_table(conversation_instance.id, subject, chapter)
    # if knowledge_content == 'Not Found':
    #     pass
    # else:
    #     conversation_instance_qs = Conversation.objects.filter(id=conversation_instance)
    #     if not conversation_instance_qs.exists():
    #         return 'Conversation not found'
    #     conversation_instance = conversation_instance_qs.first()
    #     if conversation_instance.knowledge:
    #         conversation_instance.knowledge += "\n" + knowledge_content
    #     else:
    #         conversation_instance.knowledge = knowledge_content

        # Kiểm tra và cập nhật kiến thức nếu cần thiết
    # knowledge_content = query_data_from_db_table(conversation_instance.id, subject, chapter)
    # if knowledge_content != 'Not Found':
    #     if conversation_instance.knowledge:
    #         conversation_instance.knowledge += "\n" + knowledge_content
    #     else:
    #         conversation_instance.knowledge = knowledge_content

    #     # Lưu cuộc hội thoại
    #     try:
    #         conversation_instance.save()
    #     except Exception as e:
    #         print(f"Failed to save conversation knowledge: {e}")

    
    return output['output']

def get_message_from_agent(conversation_id, user_message):
    # get conversation instance
    conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    conversation_instance = conversation_instance_qs.first()
    # get character and provider
    character = conversation_instance.prompt_name
    provider = conversation_instance.gpt_model
    # get chat history
    chat_history_dicts = conversation_instance.chat_history or []
    
    if chat_history_dicts and isinstance(chat_history_dicts[0], dict) and not chat_history_dicts[0]:
        chat_history_dicts.pop(0)
    
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]

    # run agent
    response = run_lecture_agent(
        user_message, chat_history, character=character, provider=provider, conversation_instance = conversation_instance)

    # update chat history
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": response})
    
    # conversation_instance.knowledge = response.get('knowledge', conversation_instance.knowledge)

    # save conversation instance
    try:
        conversation_instance.save()
    except Exception as e:
        print(f"Failed to save chat history: {e}")
        
    return response
