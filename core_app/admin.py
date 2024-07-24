from django.contrib import admin
from core_app.models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool
# Register your models here.

admin.site.register(Conversation)
admin.site.register(SystemPrompt)
admin.site.register(ExternalKnowledge)
admin.site.register(Agent)
admin.site.register(AgentTool)
