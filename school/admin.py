from django.contrib import admin
from .models import SchoolGrade, AcademicLoad

@admin.register(SchoolGrade)
class SchoolGradeAdmin(admin.ModelAdmin):
    list_display = ('number', 'letter', 'class_teacher')
    list_filter = ('number', 'letter')
    search_fields = ('number', 'letter', 'class_teacher__username')


@admin.register(AcademicLoad)
class AcademicLoadAdmin(admin.ModelAdmin):
    list_display = ('school_grade', 'subject', 'teacher')
    list_filter = ('school_grade', 'subject', 'teacher')
    search_fields = ('teacher__last_name', 'subject__name')