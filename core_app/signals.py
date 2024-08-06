from django.db.models.signals import post_save
from django.dispatch import receiver
from core_app.models import ExternalKnowledge, InternalKnowledge
from core_app.embedding.embedding_by_openai import get_vector_from_embedding

# Sử dụng một biến toàn cục để theo dõi 
updating_embedding = False

@receiver(post_save, sender=ExternalKnowledge)
@receiver(post_save, sender=InternalKnowledge)
def update_content_embedding(sender, instance, **kwargs):
    global updating_embedding

    if updating_embedding:
        return

    if isinstance(instance, ExternalKnowledge):
        if instance.content:
            text_content = instance.content
            embedding = get_vector_from_embedding(text_content)
            instance.content_embedding = embedding
        if instance.subject:
            subject_embedding = get_vector_from_embedding(instance.subject)
            instance.subject_embedding = subject_embedding
        if instance.chapter:
            chapter_embedding = get_vector_from_embedding(instance.chapter)
            instance.chapter_embedding = chapter_embedding

    if isinstance(instance, InternalKnowledge):
        if instance.summary:
            summary_embedding = get_vector_from_embedding(instance.summary)
            instance.summary_embedding = summary_embedding
    # Save the instance and avoid recursion
    try:
        updating_embedding = True
        instance.save()
    finally:
        updating_embedding = False
