"""
Content models for curriculum structure and learning materials.
All content is shared across schools (single knowledge base).
"""

from django.db import models
from django.conf import settings


class CurriculumClass(models.Model):
    """
    Represents a class level in the Ugandan curriculum (S1-S6).
    Managed by Super Admin only.
    """
    
    CLASS_LEVEL_CHOICES = [
        ('S1', 'Senior 1'),
        ('S2', 'Senior 2'),
        ('S3', 'Senior 3'),
        ('S4', 'Senior 4'),
        ('S5', 'Senior 5'),
        ('S6', 'Senior 6'),
    ]
    
    code = models.CharField(max_length=2, choices=CLASS_LEVEL_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(unique=True)  # For ordering S1, S2, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'curriculum_classes'
        verbose_name = 'Curriculum Class'
        verbose_name_plural = 'Curriculum Classes'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Topic(models.Model):
    """
    Represents a biology topic within a class level.
    Example: "The Cell", "Photosynthesis"
    """
    
    curriculum_class = models.ForeignKey(
        CurriculumClass,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    
    # Topic information
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField()  # Order within the class
    
    # Competences (for competence-based curriculum)
    learning_objectives = models.TextField(blank=True)
    key_concepts = models.JSONField(default=list, blank=True)  # List of key concepts
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['curriculum_class__order', 'order']
        unique_together = ['curriculum_class', 'title']
    
    def __str__(self):
        return f"{self.curriculum_class.code} - {self.title}"


class ContentNote(models.Model):
    """
    Learning notes/documents uploaded by teachers.
    These form the knowledge base for the AI tutor (RAG).
    """
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION', 'Needs Revision'),
    ]
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    
    # Authorship
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_notes'
    )
    
    # Content
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/%Y/%m/%d/')
    file_type = models.CharField(max_length=10)  # pdf, md, txt, docx
    
    # For RAG - extracted text content
    extracted_text = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)  # For vector embedding
    
    # Approval workflow
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='PENDING'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_notes'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_notes'
        verbose_name = 'Content Note'
        verbose_name_plural = 'Content Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.topic.title}"


class VideoResource(models.Model):
    """
    Video resources (embedded links) for topics.
    """
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    
    # Video information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()  # YouTube, Vimeo, etc.
    thumbnail_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Authorship
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_videos'
    )
    
    # Order
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_resources'
        verbose_name = 'Video Resource'
        verbose_name_plural = 'Video Resources'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.topic.title}"