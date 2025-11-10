from django.contrib import admin
from .models import ChatSession, ChatMessage, AdaptiveLearningLog


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'title', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['student__email', 'title']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content', 'created_at']
    list_filter = ['role']
    search_fields = ['content']


@admin.register(AdaptiveLearningLog)
class AdaptiveLearningLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'score_percentage', 'is_weak_area', 'recommended']
    list_filter = ['is_weak_area', 'recommended']
    search_fields = ['student__email', 'topic__title']