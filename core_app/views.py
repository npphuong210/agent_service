from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Conversation, SystemPrompt
from .serializers import ConversationSerializer, SystemPromptSerializer
from core_app.chat_service.simple_chat_bot import get_message_from_chatbot

from ca_vntl_helper import error_tracking_decorator


# Create CRUD API views here with Conversation models

class ConversationListCreate(generics.ListCreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

conversation_list_create = ConversationListCreate.as_view()

class ConversationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

conversion_retrieve_update_destroy = ConversationRetrieveUpdateDestroy.as_view()

class SystemPromptListCreate(generics.ListCreateAPIView):
    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer

system_prompt_list_create = SystemPromptListCreate.as_view()

class SystemPromptRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer

system_prompt_retrieve_update_destroy = SystemPromptRetrieveUpdateDestroy.as_view()


class AnswerMessage(generics.CreateAPIView):
    serializer_class = []


    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            conversation_id = data.get("conversation_id")
            message = data.get("message")
            output_ai_message = get_message_from_chatbot(conversation_id, message)

            return Response({"message": output_ai_message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)

answer_message = AnswerMessage.as_view()