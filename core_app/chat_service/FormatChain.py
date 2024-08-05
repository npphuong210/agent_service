from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import os




def load_llm_model(provider="openai"):
    if provider == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0 )
    else:
        raise Exception("LLM type not supported")
    return llm


def format_prompt():
    hashtag_schema = ResponseSchema(
        name="hashtag",
        description="The hashtag suitable with the question and answer, limited to 4 hashtags.",
    )
    summary_schema = ResponseSchema(
        name="summary",
        description="Brief summary of the answer, limited to one sentence.",
    )
    format_schema = [hashtag_schema, summary_schema]
    output_parser = StructuredOutputParser.from_response_schemas(format_schema)
    response_format = output_parser.get_format_instructions()

    system_prompt = """
                    Generate summary and hashtags based on the actual output. \n
                    Strictly follow the format to generate the output. Remember: Always follow format, no matter what happens.\n
                    """
    format_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}"),
            ("system", response_format),
        ]
    )
    return format_prompt

async def format_chain(input_text, provider="openai"):
    try:
        llm = load_llm_model(provider)
        prompt = format_prompt()
        output_parser = StrOutputParser()
        chain = llm|prompt|output_parser
        output = await chain.ainvoke({'input': input_text})
        return output
    except Exception as e:
        return f"An error occurred: {e}"