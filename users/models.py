from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'School Administrator'),
        ('director', 'Director'),
        ('head_teacher', 'Head Teacher'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Role")
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    fathers_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Patronymic")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groups',
        blank=True,
        related_name='structure_User_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='User permissions',
        blank=True,
        related_name='structure_User_permissions',
        related_query_name='user',
    )

    school_class = models.ForeignKey(
        'school.SchoolGrade',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name="School Grade",
        blank=True,
        null=True
    )

    birth_date = models.DateField(verbose_name="Birth Date", blank=True, null=True)

    parents = models.ManyToManyField(
        'self',
        blank=True,
        related_name='children',
        symmetrical=False,
        limit_choices_to={'role': 'parent'},
        verbose_name="Parents"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.username