from langchain_openai import OpenAIEmbeddings
import os
from core_app.models import Lecture
from langchain_core.retrievers import BaseRetriever
from core_app.models import Lecture, ExtractedData


embeddings_model = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))


def get_vector_from_embedding(text):

    return embeddings_model.embed_query(text)

def insert_embedding_into_db(model_class, filter_dict):
    instance_qs = model_class.objects.filter(**filter_dict)
    if not instance_qs.exists():
        return "Not Found"
    else:
        instance = instance_qs.first()
        text_content = instance.content
        embedding = get_vector_from_embedding(text_content)
        
        if isinstance(instance, Lecture):
            instance.content_embedding = embedding
        elif isinstance(instance, ExtractedData):
            summary_embedding = get_vector_from_embedding(instance.summary)
            hashtags_embedding = get_vector_from_embedding(instance.hashtags)
            instance.summary_embedding = summary_embedding
            instance.hashtags_embedding = hashtags_embedding

        instance.save()
        return {
            'content_embedding': embedding,
            'summary_embedding': instance.summary_embedding if isinstance(instance, ExtractedData) else None,
            'hashtags_embedding': instance.hashtags_embedding if isinstance(instance, ExtractedData) else None
        }


# def insert_embedding_into_db(filter_dict):
#     instance_qs = Lecture.objects.filter(**filter_dict)
#     if not instance_qs.exists():
#         return "Not Found"
#     else:
#         instance = instance_qs.first()
#         text_content = instance.content
#         embedding = get_vector_from_embedding(text_content)
#         instance.content_embedding = embedding
#         instance.save()
#         return instance.content_embedding