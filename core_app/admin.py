from django.contrib import admin
from core_app.models import Conversation, SystemPrompt, ExternalKnowledge, Agent, AgentTool, InternalKnowledge, LlmModel, FaceData
from django.contrib.auth.models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_login', 'is_staff', 'is_active')
    
admin.site.register(Conversation)
admin.site.register(SystemPrompt)
admin.site.register(InternalKnowledge)
admin.site.register(ExternalKnowledge)
admin.site.register(Agent)
admin.site.register(AgentTool)
admin.site.register(LlmModel)
admin.site.register(FaceData)