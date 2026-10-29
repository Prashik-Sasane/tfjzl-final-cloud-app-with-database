from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction

from .models import (
    Choice,
    Course,
    Question,
    Submission,
    SubmissionAnswer,
)


def index(request):
    course = Course.objects.first()

    if course:
        return redirect(
            "onlinecourse:course_details",
            course_id=course.id,
        )

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": None},
    )


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


@transaction.atomic
def submit(request, course_id):
    if request.method != "POST":
        return HttpResponseRedirect(
            reverse(
                "onlinecourse:course_details",
                args=[course_id],
            )
        )

    course = get_object_or_404(Course, pk=course_id)

    student_name = request.POST.get(
        "student_name", "Student"
    ).strip() or "Student"

    questions = Question.objects.filter(
        lesson__course=course
    ).prefetch_related("choices")

    submission = Submission.objects.create(
        course=course,
        student_name=student_name,
        score=0,
    )

    total_score = 0
    possible_score = 0

    for question in questions:
        selected_choice_id = request.POST.get(
            f"question_{question.id}"
        )

        selected_choice = None

        if selected_choice_id:
            selected_choice = question.choices.filter(
                pk=selected_choice_id
            ).first()

        selected_choices = (
            [selected_choice] if selected_choice else []
        )

        question_score = question.is_get_score(
            selected_choices
        )

        possible_score += question.grade
        total_score += question_score

        is_correct = (
            selected_choice is not None
            and selected_choice.is_correct
        )

        SubmissionAnswer.objects.create(
            submission=submission,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct,
        )

    submission.score = total_score
    submission.save(update_fields=["score"])

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        course=course,
    )

    questions = Question.objects.filter(
        lesson__course=course
    ).prefetch_related("choices")

    answers = {
        answer.question_id: answer
        for answer in submission.answers.select_related(
            "question",
            "selected_choice",
        )
    }

    selected_ids = []
    grade = 0
    possible = 0
    results = []

    for question in questions:
        answer = answers.get(question.id)

        selected_choice = (
            answer.selected_choice
            if answer else None
        )

        question_selected_ids = (
            [selected_choice.id]
            if selected_choice else []
        )

        selected_ids.extend(question_selected_ids)

        selected_choices = (
            [selected_choice]
            if selected_choice else []
        )

        question_grade = question.is_get_score(
            selected_choices
        )

        question_possible = question.grade

        grade += question_grade
        possible += question_possible

        results.append({
            "question_text": question.question_text,
            "selected_choice": (
                selected_choice.choice_text
                if selected_choice
                else "No answer selected"
            ),
            "selected_ids": question_selected_ids,
            "is_correct": bool(
                answer and answer.is_correct
            ),
            "grade": question_grade,
            "possible": question_possible,
        })

    context = {
        "course": course,
        "submission": submission,
        "results": results,
        "selected_ids": selected_ids,
        "grade": grade,
        "possible": possible,
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
