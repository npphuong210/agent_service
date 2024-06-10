from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Conversation
from .serializers import ConversationSerializer


# Create CRUD API views here with Conversation models

class ConversationListCreate(generics.ListCreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

conversation_list_create = ConversationListCreate.as_view()

class ConversationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

conversion_retrieve_update_destroy = ConversationRetrieveUpdateDestroy.as_view()

class AnswerMessage(generics.CreateAPIView):
    serializer_class = []
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            conversation_id = data.get("conversation_id")
            message = data.get("message")
            return Response({"message": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)

answer_message = AnswerMessage.as_view()