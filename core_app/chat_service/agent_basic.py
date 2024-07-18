from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from core_app.chat_service.simple_chat_bot import load_llm_model
from core_app.chat_service.tool_basic import tools
from core_app.models import Conversation, SystemPrompt, Lecture
from ca_vntl_helper import error_tracking_decorator

def isEmpty(dictionary):
    for element in dictionary:
        if element:
            return True
        return False

def convert_chat_dict_to_prompt(dict_message):
    #print(dict_message)
    #print("1")
    if isEmpty(dict_message) == False:
        if dict_message['message_type'] == 'human_message':
            #print("2")
            return HumanMessage(dict_message['content'])
        if dict_message['message_type'] == 'ai_message':
            #print("3")
            return AIMessage(dict_message['content'])
    return dict_message

def run_lecture_agent(input, chat_history, character, provider):
    # prompt search information from wikipedia (tools)
    
    system_prompt_qs = SystemPrompt.objects.filter(character=character)
    if not system_prompt_qs.exists():
        raise Exception("Character not found")
    
    # get system prompt
    system_prompt_instance = system_prompt_qs.first()
    system_prompt = system_prompt_instance.prompt
    
    lecture_qs = Lecture.objects.all()
    
    #sub_prompt = "nếu lecture data: {lecture_data} chưa có thì thực hiện các lệnh bên dưới. nếu đã có thì sử dụng nó để trả lời."
    
    subject = lecture_qs.values_list('subject', flat=True)
    chapter = lecture_qs.values_list('chapter', flat=True)
    # system prompt content
    system_prompt_content=f"""{system_prompt} 
                           Bạn sẽ truy cập danh sách được gợi ý sau: {subject}, {chapter} \n
                           Bạn sẽ hiểu nội dung câu hỏi và đưa ra subject và chapter chính xác hoặc gần đúng nhất trong database. \n
                           
                           You must use tool function 'query_data_from_db_table' to get information from database with input: 'query_data_from_db_table('subject', 'chapter')' If you don't know, answer you don't know. \n"""

    #print("system_prompt_content", system_prompt_content)
    
    # create system prompt
    system_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt_content
            ),
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

    #Lecture_data = Lecture.objects.filter(subject="vanhoc", chapter="tatden").first().content
    
    
    # invoke agent
    output = agent_executor.invoke({"input": input, "chat_history": []})

    return output['output']

@error_tracking_decorator
def get_message_from_agent(conversation_id, user_message):
    # get conversation instance
    print("inside get_message_from_agent")
    conversation_instance_qs = Conversation.objects.filter(id=conversation_id)
    if not conversation_instance_qs.exists():
        raise Exception("Conversation id not found")
    conversation_instance = conversation_instance_qs.first()

    # get character and provider
    character = conversation_instance.prompt_name
    provider = conversation_instance.gpt_model

    # get chat history
    chat_history_dicts = conversation_instance.chat_history
    #print("chat_history_dicts", chat_history_dicts)
    chat_history = [
        convert_chat_dict_to_prompt(chat_history_dict)
        for chat_history_dict in chat_history_dicts
    ]
    #print("-----------------------")
    #print(character, provider, chat_history)

    # run agent
    response = run_lecture_agent(
        user_message, chat_history, character=character, provider=provider
    )
    
    #print("output_agent--------------------------")
    #print(response)

    # update chat history
    conversation_instance.chat_history.append({"message_type": "human_message", "content": user_message})
    conversation_instance.chat_history.append({"message_type": "ai_message", "content": response}) 
    
    # save conversation instance
    conversation_instance.save()
    
    return response
