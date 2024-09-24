from io import BytesIO
from django.shortcuts import render
from rest_framework import generics, status, permissions
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from core_app.pdf_classify.vision_model import get_image_informations
from .models import Conversation, SystemPrompt, ExternalKnowledge, InternalKnowledge, Agent, AgentTool, LlmModel
from .serializers import ConversationSerializer, SystemPromptSerializer, ExternalKnowledgeSerializer, AgentSerializer, AgentToolSerializer, LlmModelSerializer, InternalKnowledgeSerializer, ExternalKnowledgePostSerializer
from core_app.chat_service.AgentMessage import get_message_from_agent, get_streaming_agent_instance
from core_app.extract import extract
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse, StreamingHttpResponse
from asgiref.sync import sync_to_async
from langchain.agents import AgentExecutor
import asyncio
import logging
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from core_app.authentication import BearerTokenAuthentication, get_user_instance_by_token
from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from core_app.pdf_classify.pdf_classify import is_scanned_pdf,  process_scanned_pdf_with_llm
from PIL import Image
from pdfminer.high_level import extract_text

def home(request):
    template = "home.html"
    context = {}
    return render(request, template, context)

# class BearerTokenAuthentication(TokenAuthentication):
#     keyword = 'Bearer'
    
# create CRUD API views here with LlmModel models
class LlmModelListCreate(generics.ListCreateAPIView):
    queryset = LlmModel.objects.all().order_by('-updated_at')
    serializer_class = LlmModelSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated] # Ensure user is authenticated
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Automatically associate the model with the current user
        
    def get_queryset(self):
        # Filter LlmModel objects to only those belonging to the logged-in user
        return LlmModel.objects.filter(user=self.request.user).order_by('-updated_at')
    
llm_list_create = LlmModelListCreate.as_view()
    
class LlmModelRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = LlmModel.objects.all().order_by('-updated_at')
    serializer_class = LlmModelSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer.save()
        
    def get_queryset(self):
        # Filter LlmModel objects to only those belonging to the logged-in user
        return LlmModel.objects.filter(user=self.request.user).order_by('-updated_at')
    

llm_retrieve_update_destroy = LlmModelRetrieveUpdateDestroy.as_view()

# Create CRUD API views here with Conversation models
class ConversationListCreate(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
   
    def perform_create(self, serializer):
        user_instance = get_user_instance_by_token(self.request)
        if user_instance:
            serializer.save(user=user_instance)
        else:
            raise PermissionDenied("User instance not found.")
    
    def post(self, request, *args, **kwargs):   
        data = request.data
        agent_id = data.get("agent_id")
        try:
            agent_instance = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return Response({"error": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        conversation = Conversation.objects.create(agent=agent_instance, user=request.user)
        conversation.save()
        return Response(self.serializer_class(conversation).data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')
 
conversation_list_create = ConversationListCreate.as_view()        

class ConversationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all().order_by('-updated_at')
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        # Trích xuất user_instance từ token
        user_instance = get_user_instance_by_token(request)
        if not user_instance:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        # Tách user_conversation từ request
        user_conversation = request.user
        # Kiểm tra quyền (phân quyền)
        if user_conversation != user_instance:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer.save()
         
    def get_queryset(self):
        # Filter Conversation objects to only those belonging to the logged-in user
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

conversion_retrieve_update_destroy = ConversationRetrieveUpdateDestroy.as_view()


# create CRUD API views here with SystemPrompt models
class SystemPromptListCreate(generics.ListCreateAPIView):
    queryset = SystemPrompt.objects.all().order_by('-updated_at')
    serializer_class = SystemPromptSerializer
    # authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    # permission_classes = [IsAuthenticated]

system_prompt_list_create = SystemPromptListCreate.as_view()

class SystemPromptRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemPrompt.objects.all().order_by('-updated_at')
    serializer_class = SystemPromptSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

system_prompt_retrieve_update_destroy = SystemPromptRetrieveUpdateDestroy.as_view()


# create CRUD API views here with Agent models
class AgentListCreate(generics.ListCreateAPIView):
    queryset = Agent.objects.all().order_by('-updated_at')
    serializer_class = AgentSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):        
        data = request.data
        agent_name = data.get("agent_name")
        llm = data.get("llm")
        llm_instance = LlmModel.objects.get(id=llm)
        tools = data.get("tools")
        prompt_id = data.get("prompt_id") or data.get("prompt")

        if prompt_id:
            prompt = SystemPrompt.objects.get(id=prompt_id)
        else:
            system_prompt_message = data.get("prompt_message")
            prompt = SystemPrompt(prompt_name=agent_name, prompt_content=system_prompt_message)
            prompt.save()
        agent = Agent.objects.create(agent_name=agent_name, llm=llm_instance, prompt=prompt, tools=tools, user = request.user)
        agent.save()
        return Response(self.serializer_class(agent).data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer.save()
        
    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user).order_by('-updated_at')


Agent_list_create = AgentListCreate.as_view()

class AgentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agent.objects.all().order_by('-updated_at')
    serializer_class = AgentSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        # Trích xuất user_instance từ token
        user_instance = get_user_instance_by_token(request)
        if not user_instance:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Tách user_conversation từ request
        user_conversation = request.user
        # Kiểm tra quyền (phân quyền)
        if user_conversation != user_instance:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer.save()
        
    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user).order_by('-updated_at')

Agent_retrieve_update_destroy = AgentRetrieveUpdateDestroy.as_view()

# create CRUD API views here with AgentTool models
class AgentToolListCreate(generics.ListCreateAPIView):
    queryset = AgentTool.objects.all().order_by('-updated_at')
    serializer_class = AgentToolSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
AgentTool_list_create = AgentToolListCreate.as_view()

class AgentToolRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = AgentTool.objects.all().order_by('-updated_at')
    serializer_class = AgentToolSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

AgentTool_retrieve_update_destroy = AgentToolRetrieveUpdateDestroy.as_view()
    
logger = logging.getLogger(__name__)
    
class AgentMessage(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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
        user = request.user
        data = request.data
        message = data.get("message")
        conversation_id = data.get("conversation_id")
        try:
            # Get response from AI
            ai_response = get_message_from_agent(conversation_id, message)      
            return Response({"ai_message": ai_response['ai_message'], "human_message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return Response({"ai_message": "Defined error", "human_message": message}, status=status.HTTP_400_BAD_REQUEST)
        
agent_answer_message = AgentMessage.as_view()

class AgentAnswerMessageStream(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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

            agent_executor, chat_history, conversation_instance = get_streaming_agent_instance(conversation_id)

            async def on_chat_model_stream():
                
                final_event = None
                
                async for event in agent_executor.astream_events({'input': message, 'chat_history': chat_history},
                    version="v1",
                ):

                    if event['event'] == 'on_chat_model_stream':

                        # if event['data']['chunk'].content == "":
                        #     continue
                        print(f"data: {event['data']['chunk'].content} \n\n")
                        yield f"data: {event['data']['chunk'].content} \n\n"
                    if event["event"] == 'on_chain_end':
                        final_event = event["data"]["output"]

                await sync_to_async(conversation_instance.chat_history.append)({"message_type": "human_message", "content": message})
                await sync_to_async(conversation_instance.chat_history.append)({"message_type": "ai_message", "content": final_event['output']})
                await sync_to_async(conversation_instance.save)()

            response = StreamingHttpResponse(on_chat_model_stream(), content_type="text/event-stream", status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache"
            
            return response

        except Exception as e:
            return Response(
                {"message": "failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

agent_answer_message_stream = AgentAnswerMessageStream.as_view()

class InternalKnowledgeList(generics.ListAPIView):
    queryset = InternalKnowledge.objects.all()
    serializer_class = InternalKnowledgeSerializer
    authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        agent_id = self.kwargs.get('agent_id')
        
        # Lọc theo user và agent (nếu có)
        return InternalKnowledge.objects.filter(user=user, agent_id=agent_id)


class ExternalKnowledgeList(generics.ListAPIView):
    queryset = ExternalKnowledge.objects.all().order_by('-updated_at')
    serializer_class = ExternalKnowledgeSerializer
    # authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    # permission_classes = [IsAuthenticated]  # Ensure user is authenticated



external_knowledge_list = ExternalKnowledgeList.as_view()

class ExternalKnowledgeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExternalKnowledge.objects.all().order_by('-updated_at')
    serializer_class = ExternalKnowledgeSerializer
    # authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    # permission_classes = [IsAuthenticated]


external_knowledge_retrieve_update_destroy = ExternalKnowledgeRetrieveUpdateDestroy.as_view()


class ExternalKnowledgePost(generics.CreateAPIView):
    # authentication_classes = [JWTAuthentication, BearerTokenAuthentication]
    # permission_classes = [IsAuthenticated]
    
    serializer_class = ExternalKnowledgePostSerializer
    
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "subject",
                openapi.IN_FORM,
                description="subject of pdf file",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "chapter",
                openapi.IN_FORM,
                description="chapter of pdf file",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                description="File to upload",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful response", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: "Bad Request - Can not upload file",
        },
        consumes=["multipart/form-data"],
    )

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("pass test")

        file = request.FILES.get('file') # binary file
        
        if file:
            name = file.name
            destination_path = f"data/{name}"
            with open(destination_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        # read pdf file by binary
        subject = request.data.get('subject')
        chapter = request.data.get('chapter')
        file = open(destination_path, 'rb')
        file_name = file.name
        pdf = file.read()
        
        if is_scanned_pdf(pdf):
            # if scanned PDF => vision LLM model
            file_name = file_name.lower()
            if file_name.endswith('.pdf'):
                print("Đây là PDF được scan.")
                vision_result = process_scanned_pdf_with_llm(pdf)
            elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                print("Đây là hình ảnh.")
                image = Image.open(BytesIO(pdf))
                vision_result = get_image_informations(image)
            else:
                print("Định dạng tệp không được hỗ trợ.")
                return None
            
            print("#"*50)
            print(vision_result)
            print("#"*50)
            
            knowledge = ExternalKnowledge(subject=subject, chapter=chapter, content=vision_result)
            knowledge.save()

            return Response({"message": "success"}, status=status.HTTP_200_OK)
            
        else:
            # if standard PDF => extract text
            print("Đây là PDF chuẩn.")
            file_like_object = BytesIO(pdf)
            text = extract_text(file_like_object)
            print("#"*50)
            print(text)
            print("#"*50)
            knowledge = ExternalKnowledge(subject=subject, chapter=chapter, content=text)
            knowledge.save()
            
            return Response({"message": "success"}, status=status.HTTP_200_OK)


external_knowledge_post = ExternalKnowledgePost.as_view()
# agent_answer_message = AgentMessage.as_view()