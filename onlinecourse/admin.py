from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Submission,
    Enrollment,
    Learner,
)


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2
    inlines = [ChoiceInline]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ("question_text", "course", "grade")
    search_fields = ("question_text",)


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title",)


class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_filter = ("name",)
    search_fields = ("name", "description")


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Enrollment)
admin.site.register(Learner)
