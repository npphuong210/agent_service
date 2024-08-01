import uuid
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField, HnswIndex
from django.utils import timezone
import pytz

# Create your models here.

# create a array that have dimension of 1536
empty_vector = [0.0]*1536

class CommonModel(models.Model):
    class Meta:
        abstract = True
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, db_index=True)
    
    def save(self, *args, **kwargs):
        utc7 = pytz.timezone('Asia/Ho_Chi_Minh')
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        self.created_at = self.created_at.astimezone(utc7)
        self.updated_at = self.updated_at.astimezone(utc7)
        super(CommonModel, self).save(*args, **kwargs)
        
# expose
class SystemPrompt(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt_name = models.CharField(max_length=100, unique=True)
    prompt_content = models.TextField()

    def __str__(self):
        return self.prompt_name

class AgentTool(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tool_name = models.CharField(max_length=100)
    args_schema = ArrayField(models.JSONField(default=dict, null=True, blank=True), default=list, null=True, blank=True)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.tool_name}"

class Agent(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100)
    llm = models.CharField(max_length=100)
    prompt = models.ForeignKey(SystemPrompt, on_delete=models.DO_NOTHING)
    tools = ArrayField(models.CharField(max_length=100), default=list, null=True, blank=True)

    def __str__(self):
        return self.agent_name
# expose
class Conversation(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING)
    chat_history = ArrayField(models.JSONField(), default=list, null=True, blank=True)
    meta_data = models.JSONField(default=dict, null=True, blank=True) # tool id

    def __str__(self):
        return f"{self.id} - with agent: {self.agent.agent_name}"

class ExternalKnowledge(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    content = models.TextField()
    content_embedding = VectorField(dimensions=1536, default=empty_vector)
    subject_embedding = VectorField(dimensions=1536, default=empty_vector)
    chapter_embedding = VectorField(dimensions=1536, default=empty_vector)

    
    class Meta:
        indexes = [
            HnswIndex(
                name='content_embedding_hnsw_idx',
                fields=['content_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            ),
            HnswIndex(
                name='subject_embedding_hnsw_idx',
                fields=['subject_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            ),
            HnswIndex(
                name='chapter_embedding_hnsw_idx',
                fields=['chapter_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            )
        ]
    

    def __str__(self):
        return f"{self.subject} - {self.chapter}"

class InternalKnowledge(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    summary = models.TextField()
    hashtags = models.TextField()
    message_output = models.TextField()
    summary_embedding = VectorField(dimensions=1536, default=empty_vector)
    hashtags_embedding = VectorField(dimensions=1536, default=empty_vector)
    
    
    class Meta:
        indexes = [
            HnswIndex(
                name='summary_embedding_hnsw_idx',
                fields=['summary_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            ),
            HnswIndex(
                name='hashtags_embedding_hnsw_idx',
                fields=['hashtags_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            )
        ]

    def __str__(self):
        return f"{self.summary} - {self.hashtags}"


