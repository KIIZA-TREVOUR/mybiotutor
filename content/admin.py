from django.contrib import admin
from .models import CurriculumClass, Topic, ContentNote, VideoResource


@admin.register(CurriculumClass)
class CurriculumClassAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'order']
    ordering = ['order']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'curriculum_class', 'order']
    list_filter = ['curriculum_class']
    search_fields = ['title', 'description']
    ordering = ['curriculum_class__order', 'order']


@admin.register(ContentNote)
class ContentNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'uploaded_by', 'approval_status', 'created_at']
    list_filter = ['approval_status', 'topic__curriculum_class']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


@admin.register(VideoResource)
class VideoResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'uploaded_by', 'created_at']
    list_filter = ['topic__curriculum_class']
    search_fields = ['title', 'description']