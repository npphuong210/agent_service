from django.contrib import admin
from core_app.models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool, InternalKnowledge
# Register your models here.
from rest_framework.authtoken.models import Token

admin.site.register(Conversation)
admin.site.register(SystemPrompt)
admin.site.register(InternalKnowledge)
admin.site.register(ExternalKnowledge)
admin.site.register(Agent)
admin.site.register(AgentTool)
admin.site.register(Token)