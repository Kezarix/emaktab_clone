from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from Kundalik import settings


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'System Administrator'),
        ('clerk', 'Ministry Employee'),
        ('helper', 'Support Staff'),
        ('director', 'School Director'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Role")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    fathers_name = models.CharField(max_length=150, verbose_name="Patronymic")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groups',
        blank=True,
        related_name='structure_user_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='User permissions',
        blank=True,
        related_name='structure_user_permissions',
        related_query_name='user',
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        if full_name:
            return f"{full_name} ({self.username})"
        return self.username


class AssessmentWork(models.Model):
    TYPE_CHOICES = [
        ('sor', 'SAT (Summative Assessment for Term unit)'),
        ('soch', 'SAQ (Summative Assessment for Quarter)'),
    ]

    calendar_lesson = models.ForeignKey(
        'students.CalendarLesson',
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name="Calendar Lesson"
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type")
    max_score = models.PositiveIntegerField(verbose_name="Max Score")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Name")

    class Meta:
        verbose_name = "Assessment Work"
        verbose_name_plural = "Assessment Works"

    def __str__(self):
        type_name = "SAT" if self.type == 'sor' else "SAQ"
        try:
            subject = self.calendar_lesson.schedule.subject.name
            group_name = self.calendar_lesson.schedule.group.name
        except AttributeError:
            subject = "Subject"
            group_name = "Class"

        return f"{type_name}: {self.name or ''} in {subject} ({group_name}) — max {self.max_score}b."

    def clean(self):
        super().clean()

        if not self.calendar_lesson_id:
            return

        schedule = self.calendar_lesson.schedule

        existing = AssessmentWork.objects.filter(
            calendar_lesson__schedule=schedule,
            type=self.type
        )

        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if self.type == 'sor':
            if existing.count() >= 3:
                raise ValidationError("Cannot create more than 3 SATs for a single subject.")

            total = existing.aggregate(total=Sum('max_score'))['total'] or 0
            if total + self.max_score > 50:
                raise ValidationError({
                    'max_score': 'Total maximum score for all SATs cannot exceed 50.'
                })

        elif self.type == 'soch':
            if self.max_score > 40:
                raise ValidationError({
                    'max_score': 'Maximum SAQ score cannot exceed 40.'
                })

            if existing.exists():
                raise ValidationError("Only one SAQ can be created.")

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            group = self.calendar_lesson.schedule.group

            if hasattr(group, 'students'):
                students = group.students.all()
            elif hasattr(group, 'student_set'):
                students = group.student_set.all()
            else:
                students = group.user_set.filter(role='student')

            AssessmentGrade.objects.bulk_create([
                AssessmentGrade(
                    student=student,
                    work=self,
                    earned_score=0
                )
                for student in students
            ])


class AssessmentGrade(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='assessment_grades', verbose_name="Student")
    work = models.ForeignKey(AssessmentWork, on_delete=models.CASCADE, related_name='grades', verbose_name="Assessment Work")
    earned_score = models.PositiveIntegerField(default=0, verbose_name="Earned Score")
    is_absent = models.BooleanField(default=False, verbose_name="Absent (Abs)")

    class Meta:
        verbose_name = "Assessment Grade"
        verbose_name_plural = "Assessment Grades"

    def clean(self):
        super().clean()
        if self.is_absent and self.earned_score > 0:
            raise ValidationError({'earned_score': "If the student was absent, the earned score must be 0."})
        if self.work_id and self.earned_score > self.work.max_score:
            raise ValidationError(
                {'earned_score': f"Score cannot exceed the maximum work score ({self.work.max_score})."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        try:
            lesson_date = self.work.calendar_lesson.date
            if lesson_date.month in [9, 10, 11]:
                t_num = 1
            elif lesson_date.month in [12, 1]:
                t_num = 2
            elif lesson_date.month in [2, 3]:
                t_num = 3
            else:
                t_num = 4

            tg, _ = TermGrade.objects.get_or_create(
                student=self.student,
                schedule=self.work.calendar_lesson.schedule,
                term=t_num
            )
            tg.save()
        except Exception:
            pass


class TermGrade(models.Model):
    TERM_CHOICES = [
        (1, '1st Quarter'),
        (2, '2nd Quarter'),
        (3, '3rd Quarter'),
        (4, '4th Quarter'),
        (5, '1st Half-Year'),
        (6, '2nd Half-Year'),
        (7, 'Annual Grade'),
    ]

    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='term_grades',
                                verbose_name="Student")
    schedule = models.ForeignKey('students.Schedule', on_delete=models.CASCADE, related_name='term_grades',
                                 verbose_name="Subject / Schedule")
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES, verbose_name="Period")

    total_sor_ball = models.FloatField(default=0.0, verbose_name="Total SAT Score")
    soch_ball = models.FloatField(default=0.0, verbose_name="SAQ Score")
    average_percent = models.FloatField(default=0.0, verbose_name="Average Percentage")
    final_mark = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Final Grade (2-5)")

    class Meta:
        verbose_name = "Final Grade"
        verbose_name_plural = "Final Grades"
        unique_together = ('student', 'schedule', 'term',)

    def calculate_totals(self):
        if self.term in [1, 2, 3, 4]:
            grades = AssessmentGrade.objects.filter(student=self.student, work__calendar_lesson__schedule=self.schedule)

            self.total_sor_ball = grades.filter(work__type='sor').aggregate(res=Sum('earned_score'))['res'] or 0
            self.soch_ball = grades.filter(work__type='soch').aggregate(res=Sum('earned_score'))['res'] or 0

            max_sor = grades.filter(work__type='sor').aggregate(res=Sum('work__max_score'))['res'] or 0
            max_soch = grades.filter(work__type='soch').aggregate(res=Sum('work__max_score'))['res'] or 0

            sor_ratio = (self.total_sor_ball / max_sor) if max_sor else 0
            soch_ratio = (self.soch_ball / max_soch) if max_soch else 0

            if max_soch:
                self.average_percent = ((sor_ratio * 50) + (soch_ratio * 40)) / 90 * 100
            else:
                self.average_percent = sor_ratio * 100
        else:
            prev_terms = [1, 2] if self.term == 5 else [3, 4] if self.term == 6 else [5, 6]
            percents = TermGrade.objects.filter(student=self.student, schedule=self.schedule,
                                                term__in=prev_terms).values_list('average_percent', flat=True)
            self.average_percent = sum(percents) / len(percents) if percents else 0

        if self.average_percent >= 85:
            self.final_mark = 5
        elif self.average_percent >= 65:
            self.final_mark = 4
        elif self.average_percent >= 40:
            self.final_mark = 3
        else:
            self.final_mark = 2

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)


class SupportChat(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_support_chat',
        verbose_name="User (Teacher/Administration)"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Activity")

    class Meta:
        verbose_name = "Support Chat"
        verbose_name_plural = "Support Chats"

    def clean(self):
        super().clean()
        if self.user_id and self.user.role not in ['teacher', 'admin', 'director']:
            raise ValidationError("Only teachers or administration can initiate a support chat.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Chat: {self.user.last_name} {self.user.first_name}"


class SupportMessage(models.Model):
    chat = models.ForeignKey(SupportChat, on_delete=models.CASCADE, related_name='messages', verbose_name="Chat")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Sender",
                               blank=True, null=True)
    text = models.TextField(verbose_name="Message Text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sent At")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def clean(self):
        super().clean()
        if not self.chat_id or not self.sender_id:
            return

        is_chat_owner = (self.sender_id == self.chat.user_id)
        is_helper = (self.sender.role in ['helper', 'admin'])

        if not is_chat_owner and not is_helper:
            raise ValidationError("Only the chat owner or support helpers can write in this chat.")

    def save(self, *args, **kwargs):
        if self.pk and self.sender_id:
            self.full_clean()
        super().save(*args, **kwargs)