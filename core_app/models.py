import uuid
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField, HnswIndex
from django.utils import timezone
from django.contrib.auth.models import User
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

class LlmModel(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    llm_name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    model_version = models.CharField(max_length=100) # gpt 3.5
    api_key = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.llm_name
    class Meta:
        unique_together = ['llm_name', 'user']

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
    llm = models.ForeignKey(LlmModel, on_delete=models.DO_NOTHING, null=True, blank=True)
    prompt = models.ForeignKey(SystemPrompt, on_delete=models.DO_NOTHING)
    tools = ArrayField(models.CharField(max_length=100), default=list, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    def __str__(self):
        return self.agent_name
    class Meta:
        unique_together = ['agent_name', 'user']

# expose
class Conversation(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING)
    chat_history = ArrayField(models.JSONField(), default=list, null=True, blank=True)
    meta_data = models.JSONField(default=dict, null=True, blank=True) # tool id
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_use_internal_knowledge = models.BooleanField(default=True)
    
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
    question = models.TextField()
    summary_embedding = VectorField(dimensions=1536, default=empty_vector)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING, null=True, blank=True)
    class Meta:
        indexes = [
            HnswIndex(
                name='summary_embedding_hnsw_idx',
                fields=['summary_embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            ),
        ]
    def __str__(self):
        return f"{self.summary}"

class FaceData(models.Model):
    # image = models.ImageField(upload_to='faces/')  # Trường lưu ảnh
    face_encoding = models.BinaryField()  # Trường lưu encoding của khuôn mặt dưới dạng nhị phân
    full_name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    birthday = models.DateField()
    gender = models.CharField(max_length=10)
    age = models.CharField(max_length=3)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=15)
    
    def __str__(self):
        return self.full_name