from rest_framework import serializers
from .models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool, LlmModel

class LlmModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LlmModel
        fields = ['id', 'llm_name', 'provider', 'model_version', 'user']  # Exclude api_key for security
        read_only_fields = ['id', 'user']  # Ensure some fields are read-only


class ConversationSerializer(serializers.ModelSerializer):
    chat_history = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    class Meta:
        model = Conversation
        fields = ['id', 'agent', 'chat_history']

class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = '__all__'

class ExternalKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalKnowledge
        fields = ['subject', 'chapter', 'content']

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        
class AgentToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentTool
        fields = '__all__'