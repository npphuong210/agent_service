from langchain_openai import OpenAIEmbeddings
import os
from core_app.models import ExternalKnowledge
from langchain_core.retrievers import BaseRetriever
from core_app.models import ExternalKnowledge, InternalKnowledge


embeddings_model = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))


def get_vector_from_embedding(text):

    return embeddings_model.embed_query(text)

def insert_embedding_into_db(model_class, filter_dict):
    instance_qs = model_class.objects.filter(**filter_dict)
    if not instance_qs.exists():
        return "Not Found"
    else:
        instance = instance_qs.first()
        instance = instance_qs.first()
        # Update content embedding
        if instance.content:
            text_content = instance.content
            content_embedding = get_vector_from_embedding(text_content)
            instance.content_embedding = content_embedding
        
        # Update subject and chapter embeddings for ExternalKnowledge
        if isinstance(instance, ExternalKnowledge):
            if instance.subject:
                subject_embedding = get_vector_from_embedding(instance.subject)
                instance.subject_embedding = subject_embedding
            if instance.chapter:
                chapter_embedding = get_vector_from_embedding(instance.chapter)
                instance.chapter_embedding = chapter_embedding

        # Update summary embeddings for InternalKnowledge
        if isinstance(instance, InternalKnowledge):
            if instance.summary:
                summary_embedding = get_vector_from_embedding(instance.summary)
                instance.summary_embedding = summary_embedding

        instance.save()
        return {
            'content_embedding': content_embedding if instance.content else None,
            'subject_embedding': subject_embedding if isinstance(instance, ExternalKnowledge) and instance.subject else None,
            'chapter_embedding': chapter_embedding if isinstance(instance, ExternalKnowledge) and instance.chapter else None,
            'summary_embedding': summary_embedding if isinstance(instance, InternalKnowledge) and instance.summary else None,
        }


# def insert_embedding_into_db(filter_dict):
#     instance_qs = ExternalKnowledge.objects.filter(**filter_dict)
#     if not instance_qs.exists():
#         return "Not Found"
#     else:
#         instance = instance_qs.first()
#         text_content = instance.content
#         embedding = get_vector_from_embedding(text_content)
#         instance.content_embedding = embedding
#         instance.save()
#         return instance.content_embedding