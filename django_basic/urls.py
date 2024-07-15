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
from core_app.views import (conversation_list_create, conversion_retrieve_update_destroy, 
                            answer_message, agent_message, 
                            system_prompt_list_create, system_prompt_retrieve_update_destroy, 
                            lecture_list_create, lecture_retrieve_update_destroy)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("conversation/", conversation_list_create, name="conversation-list-create"),
    path("conversation/<int:pk>/", conversion_retrieve_update_destroy, name="conversation-retrieve-update-destroy"),

    path("system-prompt/", system_prompt_list_create, name="system-prompt-list-create"),
    path("system-prompt/<int:pk>/", system_prompt_retrieve_update_destroy, name="system-prompt-retrieve-update-destroy"),
    
    path("lecture/", lecture_list_create, name="lecture-list-create"),
    path("lecture/<int:pk>/", lecture_retrieve_update_destroy, name="lecture-retrieve-update-destroy"),

    path("agent/", agent_message, name="agent-message"),
    #path("answer/", answer_message, name="answer-message")
]
