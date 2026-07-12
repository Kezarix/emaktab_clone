from django.contrib import admin
from .models import StudyGroup, CalendarLesson, Subject, Schedule

from django.contrib import admin
from .models import Mark


@admin.register(Mark)
class AttendanceAndGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_subject', 'get_class', 'value', 'date')

    list_filter = ('date', 'academic_load__subject', 'academic_load__school_grade')

    search_fields = ('student__first_name', 'student__last_name')

    @admin.display(description="Предмет")
    def get_subject(self, obj):
        return obj.academic_load.subject.name

    @admin.display(description="Класс")
    def get_class(self, obj):
        return f"{obj.academic_load.school_grade.number}-{obj.academic_load.school_grade.letter}"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'teacher', 'day_of_week', 'start_time' , 'classroom' )
    list_filter = ('day_of_week', 'school_class')


@admin.register(CalendarLesson)
class CalendarLessonAdmin(admin.ModelAdmin):
    list_display = ('date', 'schedule')

