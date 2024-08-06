from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from ca_vntl_helper import error_tracking_decorator
import os
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .agent_tool import tool_mapping
from core_app.models import ExternalKnowledge
from .FormatChain import format_chain
class AgentCreator:
    def __init__(self, agent_name: str, llm_type: str, prompt_content: str, tools: list[str]):
        self.agent_name = agent_name
        self.llm_type = llm_type
        self.prompt_content = prompt_content
        self.tools_str = tools

        lecture_qs = ExternalKnowledge.objects.all()
        
        subject = lecture_qs.values_list('subject', flat=True)
        chapter = lecture_qs.values_list('chapter', flat=True)


        self.hidden_prompt = f"""
                All answer must be in Vietnamese.
                Must use these tools to get information and only use 1 tool. Don't make things up. \n
                Being flexible between using the tools 'query_internal_knowledge' and 'query_external_knowledge' based on the purpose of the tools is key to success.\n
                In case the question has never been asked before or not related to the past questions, you are given a list of {subject} and {chapter} to choose from, you can use the 'query_external_knowledge' tool to get the information from the external knowledge table.\n
                In case the question has been asked before or likely related to the past questions, you can use the 'query_internal_knowledge' tool to get the information from the internal knowledge table and use that information.\n
                If i ask: 'What question/problem did i just ask before ?' or something similar, you can trace back the last question using the 'trace_back' tool.\n
                """

    def load_tools(self):
        tools = []
        for tool_str in self.tools_str:
            tools.append(tool_mapping[tool_str])
        return tools

    def load_llm(self):
        if self.llm_type == "openai":
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0 )
        else:
            raise Exception("LLM type not supported")
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
def run_chatbot(input_text, chat_history, agent_role, llm_type="openai", prompt_content="", user_tools=[]):
    agent_instance = AgentCreator(agent_name=agent_role, llm_type=llm_type, prompt_content=prompt_content,
                                  tools=user_tools)

    output_message = agent_instance.get_message_from_agent(input_text, chat_history)
    format_output = format_chain(output_message)

    return output_message, format_output
