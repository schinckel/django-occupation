from django.contrib import admin

from .models import Student, StaffMember, Subject, Enrolment, School, Result

admin.site.register(Student)
admin.site.register(StaffMember)
admin.site.register(Subject)
admin.site.register(School)
admin.site.register(Result)


class ResultInline(admin.TabularInline):
    model = Result


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    inlines = [ResultInline]
