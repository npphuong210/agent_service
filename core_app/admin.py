from django.contrib import admin
from core_app.models import Conversation, SystemPrompt
# Register your models here.

admin.site.register(Conversation)
admin.site.register(SystemPrompt)