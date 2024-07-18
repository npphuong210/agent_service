from pgvector.django import L2Distance
from core_app.models import Lecture
from core_app.embedding.embedding_by_openai import get_vector_from_embedding
def get_closest_meaning_lecture(query_content):

    query_embedding = get_vector_from_embedding(query_content)
    closest_lecture = Lecture.objects.annotate(
        distance=L2Distance("content_embedding", query_embedding)
    ).order_by("distance").first()

    return closest_lecture.subject, closest_lecture.chapter

def get_list_meaning(query_content, k=4):
    query_embedding = get_vector_from_embedding(query_content)
    lectures = Lecture.objects.annotate(
        distance=L2Distance("content_embedding", query_embedding)
    ).order_by("distance")[:k]
    return [(lecture.subject, lecture.chapter) for lecture in lectures]