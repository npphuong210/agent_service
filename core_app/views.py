from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Conversation, SystemPrompt, Lecture
from .serializers import ConversationSerializer, SystemPromptSerializer, LectureSerializer
from core_app.chat_service.simple_chat_bot import get_message_from_chatbot
from core_app.chat_service.agent_basic import get_message_from_agent, get_streaming_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from django.http import StreamingHttpResponse
import asyncio


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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["conversation_id", "message"],
            properties={
                "conversation_id": openapi.Schema(type=openapi.TYPE_INTEGER),
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
            print("response success")
            output_ai_message = get_message_from_agent(conversation_id, message)
            return Response({"ai_message": output_ai_message, "human_message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"ai_message": "Defined error", "human_message": message}, status=status.HTTP_400_BAD_REQUEST)
        
agent_answer_message = AgentMessage.as_view()


class AgentAnswerMessage(generics.GenericAPIView):
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
        try:
            print("response success")
            conversation_id = request.data.get("conversation_id")
            message = request.data.get("message")
            
            if not conversation_id or not message:
                return Response(
                    {"message": "conversation_id and message are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            output_ai_message = get_message_from_chatbot(conversation_id, message)
            return Response({"message": output_ai_message}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"message": "failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

answer_message = AgentAnswerMessage.as_view()


class AgentAnswerMessageStream(generics.GenericAPIView):
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
        try:
            print("response success")
            conversation_id = request.data.get("conversation_id")
            message = request.data.get("message")
            
            if not conversation_id or not message:
                return Response(
                    {"message": "conversation_id and message are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ai_response_generator = get_streaming_response(conversation_id, message)
            
            # ai_response = ai_response_generator['output']
            
            agent_executor, chat_history = get_streaming_response(conversation_id, message)
            
            async def on_chat_model_stream():
                num_events = 0
                async for event in agent_executor.astream_events({'input': message, 'chat_history': chat_history}, 
                    version="v1",
                ):
                    if event['event'] == 'on_chat_model_stream':
                        
                        if event['data']['chunk'].content == "":
                            continue
                        #print("--", event['data']['chunk'].content, "--")
                        yield event['data']['chunk'].content
        
                    
            #asyncio.run(on_chat_model_stream())
    
            
            # def generate_stream():
            #     async for ai_response in get_streaming_response(conversation_id, message):
            #         yield ai_response
            
            return StreamingHttpResponse(on_chat_model_stream(), content_type="text/event-stream", status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"message": "failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

streaming_message = AgentAnswerMessageStream.as_view()