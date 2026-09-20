from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import SchoolGrade, AcademicLoad

User = get_user_model()


class StudentInline(admin.TabularInline):
    model = User
    fk_name = 'school_class'
    extra = 0
    fields = ('username', 'first_name', 'last_name', 'role', 'email')
    readonly_fields = ('username',)
    verbose_name = "Student"
    verbose_name_plural = "Students in this class"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='student')


@admin.register(SchoolGrade)
class SchoolGradeAdmin(admin.ModelAdmin):
    list_display = ('number', 'letter', 'class_teacher', 'student_count')
    list_filter = ('number', 'letter')
    search_fields = ('number', 'letter', 'class_teacher__username')
    inlines = [StudentInline]

    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.students.filter(role='student').count()


@admin.register(AcademicLoad)
class AcademicLoadAdmin(admin.ModelAdmin):
    list_display = ('school_grade', 'subject', 'teacher')
    list_filter = ('school_grade', 'subject', 'teacher')
    search_fields = ('teacher__last_name', 'subject__name')