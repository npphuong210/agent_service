from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField

# Create your models here.

# create a array that have dimension of 1536
empty_vector = [0.0]*1536

class SystemPrompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character = models.CharField(max_length=100, unique=True)
    prompt = models.TextField()
    def __str__(self):
        return self.character

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character_id = models.ForeignKey(SystemPrompt, on_delete=models.CASCADE)
    gpt_model = models.CharField(max_length=100) # provider
    chat_history = ArrayField(models.JSONField(), default=list, null=True, blank=True) # {"message_type": "ai_message or human_message", "content": "hello"}
    meta_data = models.JSONField(default=dict, null=True, blank=True)
    knowledge = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

class SystemPrompt(models.Model):
    id = models.AutoField(primary_key=True)
    character = models.CharField(max_length=100, unique=True)
    prompt = models.TextField()
    def __str__(self):
        return self.character

class Lecture(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    content = models.TextField()
    content_embedding = VectorField(dimensions=1536, default=empty_vector)
    def __str__(self):
        return f"{self.subject} - {self.chapter}"


class ExtractedData(models.Model):
    id = models.AutoField(primary_key=True)
    summary = models.TextField()
    hashtags = models.TextField()
    message_output = models.TextField()
    summary_embedding = VectorField(dimensions=1536, default=empty_vector)
    hashtags_embedding = VectorField(dimensions=1536, default=empty_vector)


    def __str__(self):
        return f"{self.summary} - {self.hashtags}"