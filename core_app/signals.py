from django.db.models.signals import post_save
from django.dispatch import receiver
from core_app.models import Lecture
from core_app.embedding.embedding_by_openai import get_vector_from_embedding

# Sử dụng một biến toàn cục để theo dõi 
updating_embedding = False

@receiver(post_save, sender=Lecture)
def update_content_embedding(sender, instance, **kwargs):
    global updating_embedding

    # Kiểm tra xem việc lưu instance có phải do signal kích hoạt hay không
    if updating_embedding:
        return

    # Kiểm tra xem trường content có thay đổi hay không
    if instance.content:
        text_content = instance.content
        embedding = get_vector_from_embedding(text_content)
        instance.content_embedding = embedding

        # Tránh vòng lặp vô hạn
        updating_embedding = True
        try:
            instance.save()
        finally:
            updating_embedding = False
