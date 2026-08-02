from django.contrib import admin
from .models import AssessmentWork, AssessmentGrade, TermGrade, SupportChat, SupportMessage

admin.site.register(TermGrade)
admin.site.register(SupportChat)
admin.site.register(SupportMessage)

class AssessmentGradeInline(admin.TabularInline):
    model = AssessmentGrade
    extra = 1
    fields = ('student', 'earned_score', 'is_absent')

@admin.register(AssessmentWork)
class AssessmentWorkAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type', 'max_score')
    inlines = [AssessmentGradeInline]