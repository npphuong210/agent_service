from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from ca_vntl_helper import error_tracking_decorator
import os
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .agent_tool import tool_mapping
from core_app.models import ExternalKnowledge, LlmModel
from .FormatChain import format_chain
class AgentCreator:
    def __init__(self, agent_name: str, llm_id: str, prompt_content: str, tools: list[str]):
        self.agent_name = agent_name
        self.llm_id = llm_id
        self.prompt_content = prompt_content
        self.tools_str = tools

        lecture_qs = ExternalKnowledge.objects.all()
        
        subject = lecture_qs.values_list('subject', flat=True)
        chapter = lecture_qs.values_list('chapter', flat=True)


        self.hidden_prompt = f"""
                All answer must be in Vietnamese.\n
                
                If you can use the information from the chat_history to answer, you don't need to use the tools. If not, must use these tools to get information and only use 1 tool. Don't make things up. \n
                
                Being flexible between using the tools 'query_internal_knowledge', 'query_external_knowledge' and other tools based on the use case of the tools is key to success.\n
                
                First, try to use the 'query_internal_knowledge' tool to get information. If the question has been asked before or is likely related to past questions, use this tool. If no similar summary is found, use the 'query_external_knowledge' tool to get information from the external knowledge table using the subjects: {subject} and chapters: {chapter} provided.\n
                
                Flexibly use the tools based on the purpose of the tools to ensure success.
                
                If neither 'query_internal_knowledge' nor 'query_external_knowledge' provides the necessary information, use other tools to find the answer.
                """

    def load_tools(self):
        tools = []
        for tool_str in self.tools_str:
            tools.append(tool_mapping[tool_str])
        return tools

    def load_llm(self):
        if self.llm_id:
            try:
                # Truy vấn LlmModel để lấy thông tin mô hình
                llm_model = LlmModel.objects.get(id=self.llm_id)
                api_key = llm_model.api_key
                model_version = llm_model.model_version
                if llm_model.provider == "openai":
                    llm = ChatOpenAI(api_key=api_key, model=model_version, streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0 )
                else:
                    raise Exception("LLM provider not supported")
            except LlmModel.DoesNotExist:
                raise Exception("LlmModel with the given ID not found")
        else:
            raise Exception("LLM ID must be provided")
        return llm

    def create_system_prompt_template(self):

        system_prompt_content = self.prompt_content + "\n following the format below to generate the output. Remember: Always follow format, no matter what happens.\n" + self.hidden_prompt

        system_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_content),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
        return system_prompt

    def create_agent_runnable(self):
        system_prompt = self.create_system_prompt_template()
        llm = self.load_llm()
        tools = self.load_tools()
        agent_runnable = create_tool_calling_agent(llm, tools, system_prompt)
        return agent_runnable, tools

    def create_agent_executor(self):
        agent, tools = self.create_agent_runnable()
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor

    def get_message_from_agent(self, user_message, chat_history):
        agent_exec = self.create_agent_executor()
        output = agent_exec.invoke({"input": user_message, "chat_history": chat_history})
        return output['output']


@error_tracking_decorator
def run_chatbot(input_text, chat_history, agent_role, llm_id, prompt_content="", user_tools=[]):
    agent_instance = AgentCreator(agent_name=agent_role, llm_id=llm_id, prompt_content=prompt_content, tools=user_tools)

    output_message = agent_instance.get_message_from_agent(input_text, chat_history)
    format_output = format_chain(output_message)

    return output_message, format_output
