from django.contrib import admin
from .models import StudyGroup, CalendarLesson, Subject, Schedule

from django.contrib import admin
from .models import Mark

from .models import HomeworkSubmission


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'get_subject', 'get_lesson_date', 'get_lesson_time', 'created_at')

    list_filter = ('lesson__date', 'lesson__schedule__subject', 'created_at')

    search_fields = ('student__username', 'student__last_name', 'lesson__schedule__subject__name', 'text_answer')

    readonly_fields = ('created_at',)

    @admin.display(ordering='lesson__schedule__subject__name', description='Предмет')
    def get_subject(self, obj):
        return obj.lesson.schedule.subject.name

    @admin.display(ordering='lesson__date', description='Дата урока')
    def get_lesson_date(self, obj):
        return obj.lesson.date

    @admin.display(ordering='lesson__schedule__start_time', description='Время начала')
    def get_lesson_time(self, obj):
        return obj.lesson.schedule.start_time

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

