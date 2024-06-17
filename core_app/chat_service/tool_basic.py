from langchain_community.tools import WikipediaQueryRun, tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field


# use the wikipedia tool from langchain_community
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# tools = [wikipedia]

# create custom tools

# important part:
# name, description, args_schema

class QueryInput(BaseModel):
    query: str = Field(description="query to look up on wikipedia")

@tool("query_data_from_wikipedia", args_schema=QueryInput)
def query_data_from_wikipedia(query: str) -> str:
    """Get data from wikipedia."""
    output = WikipediaAPIWrapper().run(query)
    return output

tools = [query_data_from_wikipedia]

