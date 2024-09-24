from core_app.models import ExternalKnowledge
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
from pgvector.django import L2Distance
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os
from langchain_core.output_parsers import StrOutputParser

def create_multi_queries(user_input):
    template = """You are an AI language model assistant. Your task is to generate five 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. By generating multiple perspectives on the user question, your goal is to help
        the user overcome some of the limitations of the distance-based similarity search. 
        Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(api_key=os.getenv('API_KEY'), model='gpt-3.5-turbo', streaming=True, temperature=0, verbose=True)
    generate_queries = (
            prompt_perspectives 
            | llm
            | StrOutputParser() 
            | (lambda x: x.split("\n"))
    )
    
    multi_queries = generate_queries.invoke({"question": user_input})
    return multi_queries


def vector_search(query: str):
    embedded = get_vector_from_embedding(query)
    knowledge_qs = ExternalKnowledge.objects.annotate(
        distance=L2Distance("content_embedding", embedded)
        ).order_by("distance")[:3]
    results = [(knowledge.content, rank) for rank, knowledge in enumerate(knowledge_qs)]
    return results

def reciprocal_rank_fusion(rankings, k=60):
    from collections import defaultdict
    
    # Initialize a default dictionary to hold the aggregated scores
    score_dict = defaultdict(float)
    
    # Iterate over each ranked list
    for ranking in rankings:
        for rank, (doc, _) in enumerate(ranking):
            if doc not in score_dict:
                score_dict[doc] = 0.0
            score_dict[doc] += 1.0 / (k + rank + 1)
    
    # Sort documents by their aggregated scores in descending order
    sorted_docs = sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    #print(sorted_docs, "----------------")
    
    #print("Reranked documents: ", sorted_docs)
    
    return sorted_docs


def retrieve_documents_with_rrf(similar_queries, top_k=3):
    num_queries = 5
    all_rankings = []
    for query in similar_queries[:num_queries]:
        results = vector_search(query)
        all_rankings.append(results)
    
    combined_results = reciprocal_rank_fusion(all_rankings)
    
    top_k_combined_results = combined_results[:top_k]
    
    return top_k_combined_results


class RouteQuery(BaseModel):
    """ Route a user query to the mmost relevant data source """
    
    datasource: Literal["external", "your_knowledge"] = Field(
        ...,
        description="The data source to route the query to",
    )

class CheckValidQuery(BaseModel):
    """ Check if the query is valid """
    
    query: Literal['yes', 'no'] = Field(
        ...,
        description="The query to check",
    )


# def create_decomposition_qeury(user_input):
#     template = """You are a helpful assistant that generates multiple sub-questions related to an input question. \n
#     The goal is to break down the input into a set of sub-problems / sub-questions that can be answers in isolation. \n
#     Generate multiple search queries related to: {question} \n
#     Output (3 queries):"""
#     prompt_decomposition = ChatPromptTemplate.from_template(template)
        
#     llm = self.load_llm()
        
#     generate_queries_decomposition = ( 
#         prompt_decomposition 
#         | llm 
#         | StrOutputParser() 
#         | (lambda x: x.split("\n"))
#     )
        
#     return generate_queries_decomposition.invoke({"question": user_input})

    # def create_multi_queries(self, user_input):
    #     template = """You are an AI language model assistant. Your task is to generate five 
    #     different versions of the given user question to retrieve relevant documents from a vector 
    #     database. By generating multiple perspectives on the user question, your goal is to help
    #     the user overcome some of the limitations of the distance-based similarity search. 
    #     Provide these alternative questions separated by newlines. Original question: {question}"""
    #     prompt_perspectives = ChatPromptTemplate.from_template(template)
    #     llm = self.load_llm()
    #     generate_queries = (
    #         prompt_perspectives 
    #         | llm
    #         | StrOutputParser() 
    #         | (lambda x: x.split("\n"))
    #     )
        
    #     decision = self.database_router(user_input)
        
    #     if decision.datasource == "external":
    #         print("Routing to external data source")
    #         similar_queries =  generate_queries.invoke({"question": user_input})
            
    #         similar_queries.append(f"\noriginal query. {user_input}")
        
    #         top_knowledge = retrieve_documents_with_rrf(similar_queries)
            
    #         print(top_knowledge[0])
    
    #         context = "".join([content for content, _ in top_knowledge])
                
    #         context = f"According to the knowledge base, {context}. \n question: {user_input}"
            
    #         return context
            
    #         # valid_response = self.check_valid_retrieval_information(user_input, context)
            
    #         # print(valid_response)
            
    #         # if valid_response.query.lower() == "yes":
    #         #     print("Valid response")
    #         #     input_text = f"according to the knowledge base, {context}. \n question: {user_input}"
    #         #     return input_text 
            
    #         # else:
    #         #     print("Invalid response")
    #         #     return f"The context is not sufficient to generate an accurate answer. So, you need to answer the question by youself: {user_input}"
    #     else:
    #         print("Routing to your knowledge base")
    #         return user_input

    # def database_router(self, user_input):
    #     template = """You are an expert at routing a user question to the appropriate data source.
    #     Based on the question is referring to, route it to the relevant data source.
    #     Your Knowledge source where the question is easy to answer, You can answer it directly.
    #     In addition, External source where the question is out of scope of your knowledge base and it related some specialized fields that need the highest accuracy as much as possible.
    #     """
    #     prompt = ChatPromptTemplate.from_messages(
    #         [
    #             ("system", template),
    #             ("human", "{question}"),
    #         ]
    #     )
    #     llm = self.load_llm()
    #     structured_llm = llm.with_structured_output(RouteQuery)
    #     router = prompt | structured_llm
    #     result = router.invoke({"question": user_input})
    #     return result
    
    # def check_valid_retrieval_information(self, user_input, context):
    #     validation_prompt = ChatPromptTemplate.from_template(
    #         """
    #         You are an expert in analyzing the relevance and sufficiency of information provided for answering questions.
    #         Given the following context and question, determine whether the context is appropriate and sufficient to provide a correct and complete answer to the question.
            
    #         Context: {context}
            
    #         Question: {question}
            
    #         Please answer with "yes" or "no" at the beginning of your response.
    #         If you answer "no," provide a brief explanation in Vietnamese explaining why the context is insufficient or irrelevant.
    #         """
    #     )
        
    #     llm = self.load_llm()
    #     structured_llm = llm.with_structured_output(CheckValidQuery)
    #     validation_chain = validation_prompt | structured_llm
    #     return validation_chain.invoke({"context": context, "question": user_input})

