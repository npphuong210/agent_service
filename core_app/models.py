import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
from django.utils import timezone

# Create your models here.

# create a array that have dimension of 1536
empty_vector = [0.0]*1536

# expose
class SystemPrompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt_name = models.CharField(max_length=100, unique=True)
    prompt_content = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.prompt_name


class AgentTool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tool_name = models.CharField(max_length=100)
    args_schema = ArrayField(models.JSONField(default=dict, null=True, blank=True), default=list, null=True, blank=True)
    description = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.tool_name}"

class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100)
    llm = models.CharField(max_length=100)
    prompt = models.ForeignKey(SystemPrompt, on_delete=models.DO_NOTHING)
    tools = ArrayField(models.CharField(max_length=100), default=list, null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.agent_name
# expose
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING)
    chat_history = ArrayField(models.JSONField(), default=list, null=True, blank=True)
    meta_data = models.JSONField(default=dict, null=True, blank=True) # tool id
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.id} - with agent: {self.agent.agent_name}"

class ExternalKnowledge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    content = models.TextField()
    content_embedding = VectorField(dimensions=1536, default=empty_vector)
    subject_embedding = VectorField(dimensions=1536, default=empty_vector)
    chapter_embedding = VectorField(dimensions=1536, default=empty_vector)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.chapter}"


class InternalKnowledge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    summary = models.TextField()
    hashtags = models.TextField()
    message_output = models.TextField()
    summary_embedding = VectorField(dimensions=1536, default=empty_vector)
    hashtags_embedding = VectorField(dimensions=1536, default=empty_vector)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.summary} - {self.hashtags}"


