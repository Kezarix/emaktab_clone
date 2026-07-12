from django.db import models
from django.conf import settings
from students.models import Subject

class SchoolGrade(models.Model):
    number = models.PositiveSmallIntegerField(verbose_name="Grade Number")
    letter = models.CharField(max_length=2, verbose_name="Grade Letter")

    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='managed_class',
        verbose_name="Class Teacher"
    )

    class Meta:
        verbose_name = "School Grade"
        verbose_name_plural = "School Grades"
        unique_together = ('number', 'letter')
        ordering = ['number', 'letter']

    def __str__(self):
        return f"{self.number}-{self.letter}"


class AcademicLoad(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='academic_loads',
        verbose_name="Teacher"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='academic_loads',
        verbose_name="Subject"
    )
    school_grade = models.ForeignKey(
        SchoolGrade,
        on_delete=models.CASCADE,
        related_name='academic_loads',
        verbose_name="School Grade"
    )

    class Meta:
        verbose_name = "Academic Load"
        verbose_name_plural = "Academic Loads"
        unique_together = ('school_grade', 'subject')

    def __str__(self):
        return f"{self.school_grade} | {self.subject.name} ({self.teacher.username})"