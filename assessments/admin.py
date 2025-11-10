from django.contrib import admin
from .models import Quiz, Question, AnswerChoice, QuizAttempt


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'topic__curriculum_class']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'order', 'points']
    list_filter = ['quiz']
    search_fields = ['question_text']
    inlines = [AnswerChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'percentage', 'passed', 'completed_at']
    list_filter = ['passed', 'quiz']
    search_fields = ['student__email', 'student__first_name', 'student__last_name']