from core_app.models import ExternalKnowledge
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
from pgvector.django import L2Distance


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
            score_dict[doc] += 1.0 / (k + rank + 1)
    
    # Sort documents by their aggregated scores in descending order
    sorted_docs = sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    
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

# original_query = "What is the capital of France?"
# top_k_results = retrieve_documents_with_rrf(original_query)

# for content, score in top_k_results:
#     print(f"Content: {content}, Score: {score}")


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
