from rest_framework import generics, status, permissions
from rest_framework.response import Response
from core_app.models import Conversation, Agent
from django.contrib.auth.models import User
from core_app.chat_service.AgentMessage import get_message_from_agent, get_streaming_agent_instance
import os

class QuickAnswerMessage(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        admin_user = User.objects.get(username='admin')
        message = request.data['query']
        chat_agent_name = os.getenv('CHAT_AGENT_NAME')
        if chat_agent_name:
            agent_instance = Agent.objects.get(user=admin_user, agent_name=chat_agent_name)
        else:
            agent_instance = Agent.objects.get(user=admin_user, agent_name='bap-reception')

        conversation = Conversation.objects.create(
            agent=agent_instance,
            user=admin_user,
            is_use_internal_knowledge=False
        )
        try:
            # Get response from AI
            ai_response = get_message_from_agent(conversation.id, message)
            return Response({"response": ai_response['ai_message'], "message": "post chat successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e), "message": "I am sorry, I can not response to you"},
                            status=status.HTTP_400_BAD_REQUEST)

quick_answer_message = QuickAnswerMessage.as_view()
