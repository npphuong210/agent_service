from django.contrib import admin
from core_app.models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool, InternalKnowledge, LlmModel
# Register your models here.

admin.site.register(Conversation)
admin.site.register(SystemPrompt)
admin.site.register(InternalKnowledge)
admin.site.register(ExternalKnowledge)
admin.site.register(Agent)
admin.site.register(AgentTool)
admin.site.register(LlmModel)