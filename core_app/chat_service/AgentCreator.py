from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from ca_vntl_helper import error_tracking_decorator
import os
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .agent_tool import tool_mapping
from core_app.models import ExternalKnowledge, LlmModel
from langchain_core.output_parsers import StrOutputParser
from core_app.external.external_tool import retrieve_documents_with_rrf, RouteQuery, CheckValidQuery
from core_app.models import ExternalKnowledge
from .FormatChain import format_chain

class AgentCreator:
    def __init__(self, agent_name: str, llm_id: str, prompt_content: str, tools: list[str], user: int, agent: str, is_use_internal_knowledge: bool = True):
        self.agent_name = agent_name
        self.llm_id = llm_id
        self.prompt_content = prompt_content
        self.tools_str = tools
        self.is_use_internal_knowledge = is_use_internal_knowledge
        
        lecture_qs = ExternalKnowledge.objects.all()
        
        subject = lecture_qs.values_list('subject', flat=True)
        chapter = lecture_qs.values_list('chapter', flat=True)
        print("*"*50)
        print(f"user: {user}, agent: {agent}")
        print("*"*50)
        if is_use_internal_knowledge:
            self.hidden_prompt = f"""
                    If you can use the information from the chat_history to answer, you don't need to use the tools. If not, must use these tools to get information and only use 1 tool. Don't make things up. \n
                    Being flexible between using the tools 'query_internal_knowledge', 'query_external_knowledge' and 'trace_back' based on the use case of the tools is key to success.\n
                    Use case for 'query_external_knowledge':
                    In case the question has never been asked before or not related to the past questions, you are given a list of {subject} and {chapter} to choose from, you can use the 'query_external_knowledge' tool to get the information from the external knowledge table.\n
                    Use case for 'query_internal_knowledge' with user: {user}, agent: {agent}:
                    1/ If the question has been asked before or so similar to the past questions, you will answer the question exactly the same as the past question.\n
                    2/ If the question is likely related to the past questions, you will get the information from the internal knowledge table and use that information to help answer the question.\n
                    Use case of 'trace_back':
                    If i ask about what did i ask before or something similar, you can use the 'trace_back' tool to get the information from the past conversation and answer the question.\n
                    IMPORTANT: Always answer the question in the language of the user message. \n                
                    """
        else:
            self.hidden_prompt = f"""
                    If you can use the information from the chat_history to answer, you don't need to use the tools. If not, must use these tools to get information and only use 1 tool. Don't make things up. \n
                    Being flexible between using the tools 'query_external_knowledge'. \n
                    Use case for 'query_external_knowledge':
                    In case the question has never been asked before or not related to the past questions, you are given a list of {subject} and {chapter} to choose from, you can use the 'query_external_knowledge' tool to get the information from the external knowledge table.\n
                    IMPORTANT: Always answer the question in the language of the user message. \n
                """

    def load_tools(self):
        tools = []
        if self.is_use_internal_knowledge:
            hidden_tools = ["query_internal_knowledge", "query_external_knowledge"]
        else:
            hidden_tools = ["noop_tool"]
            
        for hidden_tool in hidden_tools:
            tools.append(tool_mapping[hidden_tool])

        for tool_str in self.tools_str:
            if tool_str in hidden_tools:
                continue
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

        system_prompt_content = self.prompt_content + "\n following the format below to generate the output. Remember: Always follow format, no matter what happens. Using vietnamese to answer\n" + self.hidden_prompt

        system_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_content),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
        return system_prompt
    
    
    def create_multi_queries(self, user_input):
        template = """You are an AI language model assistant. Your task is to generate five 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. By generating multiple perspectives on the user question, your goal is to help
        the user overcome some of the limitations of the distance-based similarity search. 
        Provide these alternative questions separated by newlines. Original question: {question}"""
        prompt_perspectives = ChatPromptTemplate.from_template(template)
        llm = self.load_llm()
        generate_queries = (
            prompt_perspectives 
            | llm
            | StrOutputParser() 
            | (lambda x: x.split("\n"))
        )
        
        decision = self.database_router(user_input)
        
        if decision.datasource == "external":
            print("Routing to external data source")
            similar_queries =  generate_queries.invoke({"question": user_input})
            
            similar_queries.append(f"\noriginal query. {user_input}")
        
            top_knowledge = retrieve_documents_with_rrf(similar_queries)
    
            context = "".join([content for content, _ in top_knowledge])
            
            #print("context", context, "\n-----")
                
            context = f"According to the knowledge base, {context}."
            
            valid_response = self.check_valid_retrieval_information(user_input, context)
            
            print(valid_response)
            
            if valid_response.query.lower() == "yes":
                print("Valid response")
                input_text = f"according to the knowledge base, {context}. \n question: {user_input}"
                return input_text 
            
            else:
                print("Invalid response")
                return f"The context is not sufficient to generate an accurate answer. So, you need to answer the question by youself: {user_input}"
        else:
            print("Routing to your knowledge base")
            return user_input

    def database_router(self, user_input):
        template = """You are an expert at routing a user question to the appropriate data source.
        Based on the question is referring to, route it to the relevant data source.
        Your Knowledge source where the question is easy to answer, You can answer it directly.
        In addition, External source where the question is out of scope of your knowledge base and it related some specialized fields that need the highest accuracy as much as possible.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                ("human", "{question}"),
            ]
        )
        llm = self.load_llm()
        structured_llm = llm.with_structured_output(RouteQuery)
        router = prompt | structured_llm
        result = router.invoke({"question": user_input})
        return result
    
    def check_valid_retrieval_information(self, user_input, context):
        validation_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert in analyzing the relevance and sufficiency of information provided for answering questions.
            Given the following context and question, determine whether the context is appropriate and sufficient to provide a correct and complete answer to the question.
            
            Context: {context}
            
            Question: {question}
            
            Please answer with "yes" or "no" at the beginning of your response.
            If you answer "no," provide a brief explanation in Vietnamese explaining why the context is insufficient or irrelevant.
            """
        )
        
        llm = self.load_llm()
        structured_llm = llm.with_structured_output(CheckValidQuery)
        validation_chain = validation_prompt | structured_llm
        return validation_chain.invoke({"context": context, "question": user_input})

        
    def create_agent_runnable(self):
        system_prompt = self.create_system_prompt_template()
        llm = self.load_llm()
        tools = self.load_tools()
        
        agent_runnable = create_tool_calling_agent(llm, tools, system_prompt)
        return agent_runnable, tools

    def create_agent_executor(self):
        agent, tools = self.create_agent_runnable()
        # Create a normal agent executor
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor        

    def get_message_from_agent(self, user_message, chat_history):
        agent_exec = self.create_agent_executor()
        print("user_message", user_message)
        output = agent_exec.invoke({"input": user_message, "chat_history": chat_history})
        return output['output']


@error_tracking_decorator
def run_chatbot(input_text, chat_history, agent_role, llm_id, prompt_content="", user_tools=[], user="User:", agent="Agent:", is_use_internal_knowledge=True):
    agent_instance = AgentCreator(agent_name=agent_role, llm_id=llm_id, prompt_content=prompt_content, tools=user_tools, user=user, agent=agent, is_use_internal_knowledge=is_use_internal_knowledge)
    input_text = agent_instance.create_multi_queries(input_text)
    output_message = agent_instance.get_message_from_agent(input_text, chat_history)
    format_output = format_chain(output_message)

    return output_message, format_output

# agent = AgentCreator(agent_name="chatbot", llm_type="openai", prompt_content="Your role do not need to use any tool. just answer based on the context", tools=[])
# input_text = "How to treat breast cancer?"
# input_text = agent.create_multi_queries(input_text)
    
# output_message = agent.get_message_from_agent(input_text, [])