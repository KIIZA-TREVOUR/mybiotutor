"""
Assessment models for quizzes and student performance tracking.
"""

from django.db import models
from django.conf import settings
from content.models import Topic


class Quiz(models.Model):
    """
    Quiz for a specific topic.
    """
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    
    # Quiz information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Settings
    pass_threshold = models.PositiveIntegerField(default=50)  # Percentage
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Authorship
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_quizzes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.topic.title}"
    
    @property
    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    """
    Multiple-choice question for a quiz.
    """
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Question content
    question_text = models.TextField()
    explanation = models.TextField(blank=True)  # Explanation for correct answer
    
    # Metadata
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class AnswerChoice(models.Model):
    """
    Answer choice for a multiple-choice question.
    """
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    
    # Choice content
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'answer_choices'
        verbose_name = 'Answer Choice'
        verbose_name_plural = 'Answer Choices'
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.choice_text[:30]}... ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAttempt(models.Model):
    """
    Student's attempt at taking a quiz.
    """
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    
    # Attempt data
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Answers (stored as JSON for flexibility)
    answers = models.JSONField(default=dict)  # {question_id: choice_id}
    
    class Meta:
        db_table = 'quiz_attempts'
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.quiz.title} ({self.percentage}%)"