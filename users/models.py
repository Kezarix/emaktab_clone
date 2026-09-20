from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'System Administrator'),
        ('clerk', 'Ministry Employee'),
        ('helper', 'Support Staff'),
        ('director', 'School Director'),
        ('head_teacher', 'Head Teacher'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Role")
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    fathers_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Patronymic")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birth Date")

    major = models.ForeignKey(
        'students.Subject',
        on_delete=models.SET_NULL,
        verbose_name="Major",
        blank=True,
        null=True,
        related_name='teachers_majoring',
    )

    school_class = models.ForeignKey(
        'school.SchoolGrade',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name="School Grade",
        blank=True,
        null=True,
    )

    parents = models.ManyToManyField(
        'self',
        blank=True,
        related_name='children',
        symmetrical=False,
        limit_choices_to={'role': 'parent'},
        verbose_name="Parents",
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groups',
        blank=True,
        related_name='custom_user_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='User permissions',
        blank=True,
        related_name='custom_user_permissions',
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

    def clean(self):
        super().clean()
        if self.role == 'teacher' and not self.major_id:
            raise ValidationError({'major': 'Major is required for teachers.'})

    def save(self, *args, **kwargs):
        if self.email == "":
            self.email = None
        super().save(*args, **kwargs)