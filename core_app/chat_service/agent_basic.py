from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor

from core_app.chat_service.simple_chat_bot import load_llm_model
from core_app.chat_service.tool_basic import tools

# prompt search information from wikipedia (tools)
system_prompt_content=("You are a helpful assistant. I can help you with information from wikipedia."
                       "You can call tool function 'query_data_from_wikipedia' to get information from wikipedia with input: 'query_data_from_wikipedia('search term')")

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

llm = load_llm_model(provider="google")

# create agent constructor
agent = create_tool_calling_agent(llm, tools, system_prompt)

# create agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

output = agent_executor.invoke({"input": "search for me manga Hunter x Hunter", "chat_history": []})

print(output)
