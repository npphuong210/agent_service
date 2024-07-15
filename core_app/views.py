from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Conversation, SystemPrompt, Lecture
from .serializers import ConversationSerializer, SystemPromptSerializer, LectureSerializer
from core_app.chat_service.simple_chat_bot import get_message_from_chatbot
from core_app.chat_service.agent_basic import get_message_from_agent

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


# create CRUD API views here with SystemPrompt models
class SystemPromptListCreate(generics.ListCreateAPIView):
    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer

system_prompt_list_create = SystemPromptListCreate.as_view()

class SystemPromptRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer

system_prompt_retrieve_update_destroy = SystemPromptRetrieveUpdateDestroy.as_view()


# create CRUD API views here with Lecture models
class LecutureListCreate(generics.ListCreateAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer

lecture_list_create = LecutureListCreate.as_view()

class LectureRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer

lecture_retrieve_update_destroy = LectureRetrieveUpdateDestroy.as_view() 


class AgentMessage(generics.CreateAPIView):
    serializer_class = []
    
    def post(self, request, *args, **kwargs):
        data = request.data
        message = data.get("message")
        conversation_id = data.get("conversation_id")
        print(message)
        try:
            output_ai_message = get_message_from_agent(conversation_id, message)
            return Response({"ai_message": output_ai_message, "human_message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"ai_message": "Defined error", "human_message": message}, status=status.HTTP_400_BAD_REQUEST)
        
agent_message = AgentMessage.as_view()


class AnswerMessage(generics.CreateAPIView):
    serializer_class = []


    def post(self, request, *args, **kwargs):
        data = request.data
        message = data.get("message")
        conversation_id = data.get("conversation_id")
        try:
            output_ai_message = get_message_from_chatbot(conversation_id, message)

            return Response({"ai_message": output_ai_message, "human_message": message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"ai_message": "Defined error", "human_message": message}, status=status.HTTP_400_BAD_REQUEST)

answer_message = AnswerMessage.as_view()

