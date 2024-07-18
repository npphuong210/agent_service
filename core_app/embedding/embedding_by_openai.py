from langchain_openai import OpenAIEmbeddings
import os
from core_app.models import Lecture
from langchain_core.retrievers import BaseRetriever

embeddings_model = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))


def get_vector_from_embedding(text):

    return embeddings_model.embed_query(text)

def insert_embedding_into_db(filter_dict):
    instance_qs = Lecture.objects.filter(**filter_dict)
    if not instance_qs.exists():
        return "Not Found"
    else:
        instance = instance_qs.first()
        text_content = instance.content
        embedding = get_vector_from_embedding(text_content)
        instance.content_embedding = embedding
        instance.save()

        return instance.content_embedding
