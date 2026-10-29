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
    Learner,
    Enrollment,
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

    student_name = request.POST.get("student_name", "").strip()

    if not student_name:
        return render(
            request,
            "onlinecourse/course_details_bootstrap.html",
            {
                "course": course,
                "error": "Please enter your name.",
            },
            status=400,
        )

    learner = Learner.objects.create(
        name=student_name,
        email="",
    )

    enrollment = Enrollment.objects.create(
        learner=learner,
        course=course,
    )

    submission = Submission.objects.create(
        enrollment=enrollment,
    )

    questions = Question.objects.filter(
        lesson__course=course
    ).prefetch_related("choices")

    for question in questions:
        selected_choice_id = request.POST.get(
            f"question_{question.id}"
        )

        selected_choice = None

        if selected_choice_id:
            selected_choice = question.choices.filter(
                pk=selected_choice_id
            ).first()

        is_correct = bool(
            selected_choice and selected_choice.is_correct
        )

        if selected_choice:
            submission.choices.add(selected_choice)

        SubmissionAnswer.objects.create(
            submission=submission,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct,
        )

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission.objects.select_related(
            "enrollment__learner",
            "enrollment__course",
        ),
        pk=submission_id,
        enrollment__course=course,
    )

    questions = Question.objects.filter(
        lesson__course=course
    ).prefetch_related("choices")

    total_score = 0
    possible_score = 0
    results = []

    answers = {
        answer.question_id: answer
        for answer in submission.answers.select_related(
            "question",
            "selected_choice",
        )
    }

    for question in questions:
        possible_score += question.grade

        selected_choices = submission.choices.filter(
            question=question
        )

        question_score = question.is_get_score(
            selected_choices
        )

        total_score += question_score

        answer = answers.get(question.id)

        results.append({
            "question_text": question.question_text,
            "selected_choice": (
                answer.selected_choice.choice_text
                if answer and answer.selected_choice
                else "No answer selected"
            ),
            "is_correct": bool(
                answer and answer.is_correct
            ),
            "question_score": question_score,
            "question_grade": question.grade,
        })

    context = {
        "course": course,
        "submission": submission,
        "learner": submission.enrollment.learner,
        "results": results,
        "total_score": total_score,
        "possible_score": possible_score,
        "score": total_score,
        "total_questions": len(results),
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
