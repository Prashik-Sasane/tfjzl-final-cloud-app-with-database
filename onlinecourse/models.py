from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    question_text = models.CharField(max_length=500)
    grade = models.IntegerField(default=1)

    def is_get_score(self, selected_choices):
        correct_choices = set(
            self.choices.filter(is_correct=True)
            .values_list("id", flat=True)
        )
        selected_ids = {
            choice.id for choice in selected_choices
        }

        if correct_choices and selected_ids == correct_choices:
            return self.grade

        return 0

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        related_name="choices",
        on_delete=models.CASCADE
    )
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Enrollment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    student_name = models.CharField(max_length=200)

    def __str__(self):
        return f"Enrollment {self.id}"


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(Choice, blank=True)

    def __str__(self):
        return f"Submission for Enrollment {self.enrollment.id}"
