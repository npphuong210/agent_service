from rest_framework import generics, status
from rest_framework.response import Response
from .models import Conversation, SystemPrompt, ExternalKnowledge, InternalKnowledge
from .serializers import ConversationSerializer, SystemPromptSerializer, ExternalKnowledgeSerializer
from core_app.chat_service.AgentMessage import get_message_from_agent
from core_app.extract import extract
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


# create CRUD API views here with ExternalKnowledge models
class LecutureListCreate(generics.ListCreateAPIView):
    queryset = ExternalKnowledge.objects.all()
    serializer_class = ExternalKnowledgeSerializer

ExternalKnowledge_list_create = LecutureListCreate.as_view()

class ExternalKnowledgeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExternalKnowledge.objects.all()
    serializer_class = ExternalKnowledgeSerializer

ExternalKnowledge_retrieve_update_destroy = ExternalKnowledgeRetrieveUpdateDestroy.as_view() 


class AgentMessage(generics.CreateAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["conversation_id", "message"],
            properties={
                "conversation_id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response("Successful response", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        message = data.get("message")
        conversation_id = data.get("conversation_id")
        try:

            # Get response from AI
            ai_response = get_message_from_agent(conversation_id, message)

            # Extract information from AI response and user message
            extracted_info = extract(ai_response, message)

            # Save the extracted information to the database
            extracted_data = InternalKnowledge(
                summary=extracted_info['summary'],
                hashtags=" ".join(extracted_info['hashtags']),
                message_output=extracted_info['message_output']
            )
            extracted_data.save()

            return Response({
                "ai_message": ai_response,
                "human_message": message,
                "summary": extracted_info['summary'],
                "hashtags": extracted_info['hashtags']
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"ai_message": "Defined error", "human_message": message}, status=status.HTTP_400_BAD_REQUEST)
        
agent_answer_message = AgentMessage.as_view()

# class AgentAnswerMessageStream(generics.GenericAPIView):
#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["conversation_id", "message"],
#             properties={
#                 "conversation_id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
#                 "message": openapi.Schema(type=openapi.TYPE_STRING),
#             },
#         ),
#         responses={
#             200: openapi.Response("Successful response", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
#             400: "Bad Request",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         try:
#             print("response success")
#             conversation_id = request.data.get("conversation_id")
#             message = request.data.get("message")

#             if not conversation_id or not message:
#                 return Response(
#                     {"message": "conversation_id and message are required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             agent_executor, chat_history, conversation_instance = get_streaming_response(conversation_id, message)

#             async def on_chat_model_stream():
#                 final_event = None
#                 async for event in agent_executor.astream_events({'input': message, 'chat_history': chat_history},
#                     version="v1",
#                 ):

#                     if event['event'] == 'on_chat_model_stream':

#                         if event['data']['chunk'].content == "":
#                             continue
#                         #print("--", event['data']['chunk'].content, "--")
#                         yield event['data']['chunk'].content
#                     if event["event"] == 'on_chain_end':
#                         final_event = event["data"]["output"]

#                 await sync_to_async(conversation_instance.chat_history.append)({"message_type": "human_message", "content": message})
#                 await sync_to_async(conversation_instance.chat_history.append)({"message_type": "ai_message", "content": final_event['output']})
#                 await sync_to_async(conversation_instance.save)()

#             return StreamingHttpResponse(on_chat_model_stream(), content_type="text/event-stream", status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"message": "failed", "error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

# streaming_message = AgentAnswerMessageStream.as_view()