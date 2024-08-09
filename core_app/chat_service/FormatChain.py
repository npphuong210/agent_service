from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import os
from langchain_core.prompts import PromptTemplate

def load_llm_model(provider="openai"):
    if provider == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0 )
    else:
        raise Exception("LLM type not supported")
    return llm

def format_chain(input_text, provider="openai"):
    response_schemas = [
        ResponseSchema(name="Summary", description="Brief summary of the input, limited to one sentence."),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    response_format = output_parser.get_format_instructions()

    template = "All summary must be in Vietnamese. Generate summary of the input. Strictly follow the format to generate the output. Remember: Always follow format, no matter what happens.\n{response_format}\n{input}"
    format_prompt = PromptTemplate(
        template = template,
        input_variables=["input"],
        partial_variables={"response_format": response_format},
    )
    try:
        llm = load_llm_model(provider)
        chain = format_prompt|llm|output_parser
        output = chain.invoke({'input': input_text})
        response_output = f"Summary: {output['Summary']}"
        return response_output
    except Exception as e:
        return f"An error occurred: {e}"