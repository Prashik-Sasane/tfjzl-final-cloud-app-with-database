from django.contrib import admin

from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Submission,
    Learner,
    Instructor,
)


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "course", "grade")
    search_fields = ("question_text",)
    list_filter = ("course",)
    inlines = [ChoiceInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Learner)
admin.site.register(Instructor)
