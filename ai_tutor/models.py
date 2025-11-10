"""
AI Tutor models for chat history and RAG interactions.
"""

from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """
    A chat session between a student and the AI tutor.
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    
    # Session info
    title = models.CharField(max_length=255, blank=True)  # Auto-generated from first message
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.id} - {self.student.get_full_name()}"


class ChatMessage(models.Model):
    """
    Individual message in a chat session.
    """
    
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ASSISTANT', 'Assistant'),
        ('SYSTEM', 'System'),
    ]
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    # Message content
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # RAG metadata (for assistant messages)
    sources_used = models.JSONField(default=list, blank=True)  # List of ContentNote IDs
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AdaptiveLearningLog(models.Model):
    """
    Logs for adaptive learning recommendations.
    Tracks which topics students struggled with.
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adaptive_logs'
    )
    
    topic = models.ForeignKey(
        'content.Topic',
        on_delete=models.CASCADE,
        related_name='adaptive_logs'
    )
    
    # Performance data
    quiz_attempt = models.ForeignKey(
        'assessments.QuizAttempt',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_weak_area = models.BooleanField(default=False)
    
    # Recommendation status
    recommended = models.BooleanField(default=False)
    recommendation_shown = models.BooleanField(default=False)
    topic_reviewed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'adaptive_learning_logs'
        verbose_name = 'Adaptive Learning Log'
        verbose_name_plural = 'Adaptive Learning Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.topic.title} ({self.score_percentage}%)"