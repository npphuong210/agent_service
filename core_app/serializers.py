from rest_framework import serializers
from .models import Conversation, SystemPrompt, ExternalKnowledge

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
        fields = '__all__'