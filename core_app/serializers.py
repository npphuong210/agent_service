from rest_framework import serializers
from .models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool, LlmModel, InternalKnowledge

class LlmModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LlmModel
        fields = ['id', 'llm_name', 'provider', 'model_version', 'api_key']
        read_only_fields = ['id','user']


class ConversationSerializer(serializers.ModelSerializer):
    chat_history = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    class Meta:
        model = Conversation
        fields = '__all__'

class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = '__all__'

class ExternalKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalKnowledge
        fields = ['id', 'subject', 'chapter', 'content']

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        
class AgentToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentTool
        fields = '__all__'
        
class InternalKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalKnowledge
        fields = '__all__'

        
class ExternalKnowledgePostSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True)
    chapter = serializers.CharField(required=True)
    file = serializers.FileField(required=True)