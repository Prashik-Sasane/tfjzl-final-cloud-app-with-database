from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import (
    Course,
    Question,
    Choice,
    Submission,
    Enrollment,
    Learner,
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


@require_POST
@transaction.atomic
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    student_name = request.POST.get(
        "student_name", ""
    ).strip()

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

    # Retrieve or create the learner.
    learner, _ = Learner.objects.get_or_create(
        name=student_name,
        defaults={"email": ""},
    )

    # Retrieve or create the enrollment.
    enrollment, _ = Enrollment.objects.get_or_create(
        learner=learner,
        course=course,
    )

    # Create the submission for this enrollment.
    submission = Submission.objects.create(
        enrollment=enrollment,
    )

    # Retrieve all questions belonging to the course.
    questions = Question.objects.filter(
        course=course
    ).prefetch_related("choice_set")

    # Associate the selected Choice objects with the submission.
    for question in questions:
        selected_choice_id = request.POST.get(
            f"question_{question.id}"
        )

        if not selected_choice_id:
            continue

        selected_choice = question.choice_set.filter(
            pk=selected_choice_id
        ).first()

        if selected_choice:
            submission.choices.add(selected_choice)

    return redirect(
        "onlinecourse:show_exam_result",
        submission_id=submission.id,
    )


def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related(
            "enrollment__course",
            "enrollment__learner",
        ),
        pk=submission_id,
    )

    course = submission.enrollment.course

    questions = Question.objects.filter(
        course=course
    ).prefetch_related("choice_set")

    selected_ids = list(
        submission.choices.values_list("id", flat=True)
    )

    grade = 0
    possible = 0
    results = []

    for question in questions:
        selected_choices = submission.choices.filter(
            question=question
        )

        question_grade = question.is_get_score(
            selected_choices.values_list("id", flat=True)
        )

        grade += question_grade
        possible += question.grade

        results.append({
            "question_text": question.question_text,
            "selected_ids": list(
                selected_choices.values_list("id", flat=True)
            ),
            "grade": question_grade,
            "possible": question.grade,
        })

    context = {
        "course": course,
        "submission": submission,
        "learner": submission.enrollment.learner,
        "selected_ids": selected_ids,
        "grade": grade,
        "possible": possible,
        "results": results,
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
