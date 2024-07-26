"""django_basic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from core_app.views import (conversation_list_create, conversion_retrieve_update_destroy,  
                            system_prompt_list_create, system_prompt_retrieve_update_destroy,
                            external_knowledge_list_create, external_knowledge_retrieve_update_destroy,
                            Agent_list_create, Agent_retrieve_update_destroy,
                            AgentTool_list_create, AgentTool_retrieve_update_destroy,
                            agent_answer_message)

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API for chatbot",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("conversation/", conversation_list_create, name="conversation-list-create"),
    path("conversation/<uuid:pk>/", conversion_retrieve_update_destroy, name="conversation-retrieve-update-destroy"),

    path("system-prompt/", system_prompt_list_create, name="system-prompt-list-create"),
    path("system-prompt/<uuid:pk>/", system_prompt_retrieve_update_destroy, name="system-prompt-retrieve-update-destroy"),
    
    path("external-knowledge/", external_knowledge_list_create, name="external-knowledge-list-create"),
    path("external-knowledge/<uuid:pk>/", external_knowledge_retrieve_update_destroy, name="external-knowledge-retrieve-update-destroy"),
    
    path("agent/", Agent_list_create, name="agent-list-create"),
    path("agent/<uuid:pk>/", Agent_retrieve_update_destroy, name="agent-retrieve-update-destroy"),
    path("agent-tool/", AgentTool_list_create, name="agent-tool-list-create"),
    path("agent-tool/<uuid:pk>/", AgentTool_retrieve_update_destroy, name="agent-tool-retrieve-update-destroy"),

    #path("streaming/", streaming_message, name="streaming-message"),
    path("answer/", agent_answer_message, name="agent-answer-message"),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
