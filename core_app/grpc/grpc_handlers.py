import grpc
# grpc handlers
from concurrent import futures
from core_app.grpc.pb import Agent_pb2
from core_app.grpc.pb import Agent_pb2_grpc
from core_app.grpc.pb import AgentTool_pb2
from core_app.grpc.pb import AgentTool_pb2_grpc
from core_app.grpc.pb import Conversation_pb2
from core_app.grpc.pb import Conversation_pb2_grpc
from core_app.grpc.pb import ExternalKownledge_pb2
from core_app.grpc.pb import ExternalKownledge_pb2_grpc
from core_app.grpc.pb import InternalKownledge_pb2
from core_app.grpc.pb import InternalKownledge_pb2_grpc
from core_app.grpc.pb import LlmModel_pb2
from core_app.grpc.pb import LlmModel_pb2_grpc
from core_app.grpc.pb import SystemPrompt_pb2
from core_app.grpc.pb import SystemPrompt_pb2_grpc
from core_app.grpc.pb import User_pb2
from core_app.grpc.pb import User_pb2_grpc
from core_app.grpc.pb import UUID_pb2
from core_app.grpc.pb import UUID_pb2_grpc
# django models
from core_app.models import SystemPrompt as SystemPromptModel, Agent, AgentTool, Conversation, ExternalKnowledge, InternalKnowledge, LlmModel
from core_app.views import system_prompt_list_create
from core_app.serializers import SystemPromptSerializer
import pytz
import datetime
utc7 = pytz.timezone('Asia/Ho_Chi_Minh')

class SystemPromptControllerServicer(SystemPrompt_pb2_grpc.SystemPromptControllerServicer):
    
    def CreateSystemPrompt(self, request, context):
        try:
            system_prompt = SystemPromptModel.objects.create(
                id = request.systemprompt.id.value,
                prompt_name = request.systemprompt.prompt_name,
                prompt_content = request.systemprompt.prompt_content
            )
            system_prompt.save()  
            return SystemPrompt_pb2.CreateSystemPromptResponse(id=request.systemprompt.id)
        except Exception as e:
            return SystemPrompt_pb2.CreateSystemPromptResponse(id=request.systemprompt.id)
    
    def GetSystemPrompt(self, request, context):
        sp = SystemPrompt_pb2.SystemPrompt()
        try: 
            system_prompt_qs = SystemPromptModel.objects.filter(id=request.id.value)
            system_prompt = system_prompt_qs.first()
            
            print(system_prompt.id)
            
            
            sp.id.value = str(system_prompt.id)
            sp.prompt_name = system_prompt.prompt_name
            sp.prompt_content = system_prompt.prompt_content

                
            print(system_prompt.prompt_content, system_prompt.prompt_name, system_prompt.id)    
            
            return SystemPrompt_pb2.GetSystemPromptResponse(systemprompt=sp)
        except Exception as e:
            print('dds')
            return SystemPrompt_pb2.GetSystemPromptResponse(systemprompt=sp)
    
    def ListSystemPrompts(self, request, context):
        list_systemprompt = SystemPrompt_pb2.ListSystemPromptsResponse()
        try: 
            system_prompt = SystemPromptModel.objects.all()
            
            for sp in system_prompt:
                temp = list_systemprompt.systemprompts.add()
                temp.id.value = str(sp.id)
                temp.prompt_name = sp.prompt_name
                temp.prompt_content = sp.prompt_content
                
            return list_systemprompt
        except Exception as e:
            return list_systemprompt
    

    def UpdateSystemPrompt(self, request, context):
        try:
            system_prompt_dj_qs = SystemPromptModel.objects.filter(id=request.systemprompt.id.value)
            system_prompt_dj = system_prompt_dj_qs.first()

            system_prompt_dj.prompt_content = request.systemprompt.prompt_content
            system_prompt_dj.prompt_name = request.systemprompt.prompt_name
            system_prompt_dj.created_at = datetime.datetime.now()
            
            system_prompt_dj.save() 
            
            return SystemPrompt_pb2.UpdateSystemPromptResponse()

        except Exception as e:
            return SystemPrompt_pb2.UpdateSystemPromptResponse()
    
    def DeleteSystemPrompt(self, request, context):
        try:
            system_prompt_dj_qs = SystemPromptModel.objects.filter(id=request.id.value)
            system_prompt_dj_qs.delete()

            return SystemPrompt_pb2.DeleteSystemPromptResponse()
        except Exception as e:
            return SystemPrompt_pb2.DeleteSystemPromptResponse()
    


# class LlmModelControllerServicer(object):
    
#     def CreateLlmModel(self, request, context):


#     def GetLlmModel(self, request, context):


#     def ListLlmModels(self, request, context):


#     def UpdateLlmModel(self, request, context):


#     def DeleteLlmModel(self, request, context):

    
# class InternalKnowledgeControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateInternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetInternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListInternalKnowledges(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateInternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteInternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

# class ExternalKnowledgeControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateExternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetExternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListExternalKnowledges(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateExternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteExternalKnowledge(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')


# class ConversationControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateConversation(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetConversation(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListConversations(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateConversation(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteConversation(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

# class AgentToolControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateAgentTool(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetAgentTool(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListAgentTools(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateAgentTool(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteAgentTool(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

# class AgentControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateAgent(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetAgent(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListAgents(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateAgent(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteAgent(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

# class UserControllerServicer(object):
#     """Missing associated documentation comment in .proto file."""

#     def CreateUser(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def GetUser(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def ListUsers(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def UpdateUser(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')

#     def DeleteUser(self, request, context):
#         """Missing associated documentation comment in .proto file."""
#         context.set_code(grpc.StatusCode.UNIMPLEMENTED)
#         context.set_details('Method not implemented!')
#         raise NotImplementedError('Method not implemented!')