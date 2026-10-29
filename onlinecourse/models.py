from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="lessons",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Learner(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    learner = models.ForeignKey(
        Learner,
        related_name="enrollments",
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name="enrollments",
        on_delete=models.CASCADE
    )
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner} - {self.course}"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        related_name="questions",
        on_delete=models.CASCADE
    )
    question_text = models.CharField(max_length=500)
    grade = models.IntegerField(default=1)

    def is_get_score(self, selected_choices):
        """
        Return the question's grade if the selected choices are correct;
        otherwise return zero.

        selected_choices should contain the Choice objects selected
        for this question.
        """
        correct_choices = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
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


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        related_name="submissions",
        on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(
        Choice,
        related_name="submissions",
        blank=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission {self.pk} - {self.enrollment}"


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="answers",
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.question_text} -> {self.selected_choice}"


class Instructor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name
