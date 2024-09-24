import os
from typing import Literal
from langchain_community.graphs import Neo4jGraph # type: ignore
from langchain_experimental.graph_transformers import LLMGraphTransformer # type: ignore
from langchain_openai import ChatOpenAI # type: ignore
from langchain_core.documents import Document # type: ignore
from langchain.output_parsers import ResponseSchema, StructuredOutputParser # type: ignore
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate # type: ignore
from pydantic import BaseModel, Field


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0)

class InsightRouterQuery(BaseModel):
    """Route a user's query and LLM's answer to know whether have they insight or not"""
    isinsight: Literal['yes', 'no'] = Field(
        ...,
        description = 'given a QA pair decides that it has insight or not',
    )

def HasInsight(Q, A):
    structure_llm = llm.with_structured_output(InsightRouterQuery)
    system = "You are an expert at deciding a QA pair has insight or not"
    prompt = ChatPromptTemplate.from_messages([
        ('system', system),
        ('human', "{question}")
    ])
    
    router = prompt | structure_llm
    question = f"QA pair: \nQ:{Q} \nA:{A}"
    result = router.invoke({"question": question})
    return result.isinsight

def get_insight_QA(user_message, answer):
    
    template = "Your role gets important information from QA pair below and add proper context make sure it better for graph embedding and remember: context you added that it is true from QA. \
        \nQ: {question} \nA: {answer} \
        "
    format_prompt = PromptTemplate(
        template = template,
        input_variables=["question", "answer"],
    )
    chain = format_prompt | llm 
    output = chain.invoke({'question' :  user_message, 'answer': answer})
    return output.content


def graph_embedding(user_id, user_message, answer):
    isinsight = HasInsight(user_message, answer)
    if isinsight == 'no':
        insight = get_insight_QA(user_message, answer)
        lm_transformer = LLMGraphTransformer(llm=llm)
        graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"))
        content = f"""
        user_{user_id} has information: {insight}
        """
        doc = [Document(page_content=content)]
        graph_doc = lm_transformer.convert_to_graph_documents(doc)
        graph.add_graph_documents(graph_doc)
        print("Has isinsight")
        return True
    
    else:
        print("Do not have insight")
        return False
    