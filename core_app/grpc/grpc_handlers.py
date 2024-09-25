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
from core_app.models import \
    SystemPrompt as SystemPromptModel, \
    Agent as AgentModel, \
    AgentTool as AgentToolModel, \
    Conversation as ConversationModel, \
    ExternalKnowledge as ExternalKnowledgeModel, \
    InternalKnowledge as InternalKnowledgeModel, \
    LlmModel as LlmModelModel 
    
from django.contrib.auth.models import User as UserModel

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
    


class LlmModelControllerServicer(LlmModel_pb2_grpc.LlmModelControllerServicer):
    
    def CreateLlmModel(self, request, context):
        print(request)
        try:
            usermodel = UserModel.objects.get(id=request.llmmodel.user_id.value)
            print(usermodel)
            llm_model_dj = LlmModelModel.objects.create(
                llm_name = request.llmmodel.llm_name,
                provider = request.llmmodel.provider,
                model_version = request.llmmodel.model_version,
                api_key = request.llmmodel.api_key,
                user = usermodel
            )
            llm_model_dj.save()  
            return LlmModel_pb2.CreateLlmModelResponse(id=request.llmmodel.id)
        except Exception as e:
            return LlmModel_pb2.CreateLlmModelResponse(id=request.llmmodel.id)

    def GetLlmModel(self, request, context):
        lm = LlmModel_pb2.LlmModel()
        try: 
            llm_model_qs = LlmModelModel.objects.filter(id=request.id.value)
            
            llm_model = llm_model_qs.first()
            
            lm.id.value = str(llm_model.id)
            lm.llm_name = llm_model.llm_name
            lm.provider = llm_model.provider
            lm.model_version = llm_model.model_version
            lm.api_key = llm_model.api_key
            lm.user_id.value = str(llm_model.user.id)  
            
            return LlmModel_pb2.GetLlmModelResponse(llmmodel=lm)
        except Exception as e:
            return LlmModel_pb2.GetLlmModelResponse(llmmodel=lm)
    

    def ListLlmModels(self, request, context):
        list_llmmodel = LlmModel_pb2.ListLlmModelsResponse()
        try: 
            llm_model = LlmModelModel.objects.all()
            
            for lm in llm_model:
                temp = list_llmmodel.llmmodels.add()
                temp.id.value = str(lm.id)
                temp.llm_name = lm.llm_name
                temp.provider = lm.provider
                temp.model_version = lm.model_version
                temp.api_key = lm.api_key
                temp.user_id.value = str(lm.user.id)
                
            return list_llmmodel
        except Exception as e:
            return list_llmmodel

    def UpdateLlmModel(self, request, context):
        try:
            llm_model_dj_qs = LlmModelModel.objects.filter(id=request.llmmodel.id.value)
            llm_model_dj = llm_model_dj_qs.first()
            llm_model_dj.llm_name = request.llmmodel.llm_name
            llm_model_dj.provider = request.llmmodel.provider
            llm_model_dj.model_version = request.llmmodel.model_version
            llm_model_dj.api_key = request.llmmodel.api_key
            llm_model_dj.user.id = request.llmmodel.user_id.value
            llm_model_dj.created_at = datetime.datetime.now()
            llm_model_dj.save() 
            
            return LlmModel_pb2.UpdateLlmModelResponse()

        except Exception as e:
            print('eerr')
            return LlmModel_pb2.UpdateLlmModelResponse()

    def DeleteLlmModel(self, request, context):
        try:
            llm_model_dj_qs = LlmModelModel.objects.filter(id=request.id.value)
            llm_model_dj_qs.delete()

            return LlmModel_pb2.DeleteLlmModelResponse()
        except Exception as e:
            return LlmModel_pb2.DeleteLlmModelResponse()
    
    
# class InternalKnowledgeControllerServicer(object):

#     def CreateInternalKnowledge(self, request, context):


#     def GetInternalKnowledge(self, request, context):


#     def ListInternalKnowledges(self, request, context):


#     def UpdateInternalKnowledge(self, request, context):


#     def DeleteInternalKnowledge(self, request, context):


# class ExternalKnowledgeControllerServicer(object):

#     def CreateExternalKnowledge(self, request, context):


#     def GetExternalKnowledge(self, request, context):


#     def ListExternalKnowledges(self, request, context):


#     def UpdateExternalKnowledge(self, request, context):


#     def DeleteExternalKnowledge(self, request, context):



# class ConversationControllerServicer(object):

# class ConversationControllerServicer(LlmModel_pb2_grpc.ConversationControllerServicer):
    
#     def CreateConversation(self, request, context):
#         try:
#             usermodel = UserModel.objects.get(id=request.llmmodel.user_id.value)
#             print(usermodel)
#             conversation_dj = ConversationModel.objects.create(
#                 llm_name = request.llmmodel.llm_name,
#                 provider = request.llmmodel.provider,
#                 model_version = request.llmmodel.model_version,
#                 api_key = request.llmmodel.api_key,
#                 user = usermodel
#             )
#             llm_model_dj.save()  
#             return LlmModel_pb2.CreateLlmModelResponse(id=request.llmmodel.id)
#         except Exception as e:
#             return LlmModel_pb2.CreateLlmModelResponse(id=request.llmmodel.id)

#     def GetConversation(self, request, context):
#         lm = LlmModel_pb2.LlmModel()
#         try: 
#             llm_model_qs = LlmModelModel.objects.filter(id=request.id.value)
            
#             llm_model = llm_model_qs.first()
            
#             lm.id.value = str(llm_model.id)
#             lm.llm_name = llm_model.llm_name
#             lm.provider = llm_model.provider
#             lm.model_version = llm_model.model_version
#             lm.api_key = llm_model.api_key
#             lm.user_id.value = str(llm_model.user.id)  
            
#             return LlmModel_pb2.GetLlmModelResponse(llmmodel=lm)
#         except Exception as e:
#             return LlmModel_pb2.GetLlmModelResponse(llmmodel=lm)
    

#     def ListConversations(self, request, context):
#         list_llmmodel = LlmModel_pb2.ListLlmModelsResponse()
#         try: 
#             llm_model = LlmModelModel.objects.all()
            
#             for lm in llm_model:
#                 temp = list_llmmodel.llmmodels.add()
#                 temp.id.value = str(lm.id)
#                 temp.llm_name = lm.llm_name
#                 temp.provider = lm.provider
#                 temp.model_version = lm.model_version
#                 temp.api_key = lm.api_key
#                 temp.user_id.value = str(lm.user.id)
                
#             return list_llmmodel
#         except Exception as e:
#             return list_llmmodel

#     def UpdateConversation(self, request, context):
#         try:
#             llm_model_dj_qs = LlmModelModel.objects.filter(id=request.llmmodel.id.value)
#             llm_model_dj = llm_model_dj_qs.first()
#             llm_model_dj.llm_name = request.llmmodel.llm_name
#             llm_model_dj.provider = request.llmmodel.provider
#             llm_model_dj.model_version = request.llmmodel.model_version
#             llm_model_dj.api_key = request.llmmodel.api_key
#             llm_model_dj.user.id = request.llmmodel.user_id.value
#             llm_model_dj.created_at = datetime.datetime.now()
#             llm_model_dj.save() 
            
#             return LlmModel_pb2.UpdateLlmModelResponse()

#         except Exception as e:
#             print('eerr')
#             return LlmModel_pb2.UpdateLlmModelResponse()

#     def DeleteConversation(self, request, context):
#         try:
#             llm_model_dj_qs = LlmModelModel.objects.filter(id=request.id.value)
#             llm_model_dj_qs.delete()

#             return LlmModel_pb2.DeleteLlmModelResponse()
#         except Exception as e:
#             return LlmModel_pb2.DeleteLlmModelResponse()
    



# class AgentToolControllerServicer(object):

#     def CreateAgentTool(self, request, context):


#     def GetAgentTool(self, request, context):


#     def ListAgentTools(self, request, context):


#     def UpdateAgentTool(self, request, context):


#     def DeleteAgentTool(self, request, context):


# class AgentControllerServicer(object):

#     def CreateAgent(self, request, context):
#         try:
#             agent_dj = AgentModel.objects.create(
#                 id = request.agent.id.value,
#                 agent_name = request.agent.agent_name,
#                 tools = request.agent.tools,
#                 llm = request.agent.llm,
#                 prompt = request.agent.prompt,
#                 user = request.agent.user,
#             )
#             agent_dj.save()  
#             return Agent_pb2.CreateAgentResponse(id=request.user.id)
#         except Exception as e:
#             return Agent_pb2.CreateAgentResponse(id=request.user.id)
        
#     def GetAgent(self, request, context):

#     def ListAgents(self, request, context):

#     def UpdateAgent(self, request, context):

#     def DeleteAgent(self, request, context):

class UserControllerServicer(User_pb2_grpc.UserControllerServicer):

    def CreateUser(self, request, context):
        try:
            user_dj = UserModel.objects.create(
                #id = request.user.id.value,
                username = request.user.username,
                # password = request.user.password,
                email = request.user.email,
            )
            user_dj.set_password(request.user.password)
            user_dj.save()  
            return User_pb2.CreateUserResponse(id=request.user.id)
        except Exception as e:
            return User_pb2.CreateUserResponse(id=request.user.id)

    def GetUser(self, request, context):
        u = User_pb2.User()
        try: 
            user_dj_qs = UserModel.objects.filter(id=request.id.value)
            user_dj = user_dj_qs.first()
            
            u.id.value = str(user_dj.id)
            u.username = user_dj.username
            u.password = user_dj.password
            u.email = user_dj.email

            return User_pb2.GetUserResponse(user=u)
        except Exception as e:
            print('dds')
            return User_pb2.GetUserResponse(user=u)
    

    def ListUsers(self, request, context):
        list_user = User_pb2.ListUsersResponse()
        try: 
            user = UserModel.objects.all()
            
            for u in user:
                temp = list_user.users.add()
                temp.id.value = str(u.id)
                temp.username = u.username
                temp.password = u.password
                temp.email = u.email

            return list_user
        except Exception as e:
            return list_user

    def UpdateUser(self, request, context):
        try:
            user_dj_qs = UserModel.objects.filter(id=request.user.id.value)
            user_dj = user_dj_qs.first()

            user_dj.username = request.user.username
            user_dj.password = request.user.password
            user_dj.email = request.user.email
            user_dj.created_at = datetime.datetime.now()
            
            user_dj.save() 
            
            return User_pb2.UpdateUserResponse()

        except Exception as e:
            return User_pb2.UpdateUserResponse()


    def DeleteUser(self, request, context):
        try:
            user_dj_qs = UserModel.objects.filter(id=request.id.value)
            user_dj_qs.delete()

            return User_pb2.DeleteUserResponse()
        except Exception as e:
            return User_pb2.DeleteUserResponse()