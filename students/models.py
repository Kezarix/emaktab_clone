from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Subject Name")

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name


class StudyGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Group Name")  # e.g., English Group 1
    school_class = models.ForeignKey('school.SchoolGrade', on_delete=models.CASCADE, related_name='study_groups', verbose_name="School Grade")

    class Meta:
        verbose_name = "Study Group"
        verbose_name_plural = "Study Groups"

    def __str__(self):
        return f"{self.name} ({self.school_class})"


class Schedule(models.Model):
    DAY_CHOICES = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    school_class = models.ForeignKey('school.SchoolGrade', on_delete=models.CASCADE, related_name='schedules', verbose_name="School Grade")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules', verbose_name="Subject")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'teacher'},
        related_name='teacher_schedules',
        verbose_name="Teacher"
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="Day of the Week")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    classroom = models.CharField(max_length=50, blank=True, null=True, verbose_name="Classroom")

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        unique_together = ('school_class', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.school_class} | {self.subject.name}"


class CalendarLesson(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='calendar_lessons', null=True, blank=True, verbose_name="Schedule")
    date = models.DateField(verbose_name="Lesson Date")
    topic = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lesson Topic")
    homework = models.TextField(blank=True, null=True, verbose_name="Homework (Text)")
    homework_file = models.FileField(blank=True, null=True, verbose_name="Homework (File)")
    homework_url = models.URLField(blank=True, null=True, verbose_name="Homework (URL)")

    def clean(self):
        super().clean()
        # Validation checks only if the user provides partial/empty homework details where required
        if not self.homework and not self.homework_file and not self.homework_url:
            raise ValidationError("You must fill in at least one homework field: text, file, or URL.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Calendar Lesson"
        verbose_name_plural = "Calendar Lessons"
        unique_together = ('schedule', 'date')

    def __str__(self):
        if self.schedule:
            return f"{self.date} | {self.schedule.subject.name} | {self.schedule.school_class}"
        return f"{self.date} | No Schedule"


class Mark(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='marks',
        verbose_name="Student"
    )
    academic_load = models.ForeignKey(
        'school.AcademicLoad',
        on_delete=models.PROTECT,
        related_name='marks',
        verbose_name="Academic Load"
    )
    value = models.CharField(max_length=10, verbose_name="Grade / Mark")
    date = models.DateField(verbose_name="Date")
    is_present = models.BooleanField(default=False, verbose_name="Is Present")

    class Meta:
        verbose_name = "Grade and Attendance"
        verbose_name_plural = "Grades and Attendance"
        unique_together = ('student', 'academic_load', 'date')

    def __str__(self):
        return f"{self.student.last_name} — {self.academic_load.subject.name}: {self.value}"

