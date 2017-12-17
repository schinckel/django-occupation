from django.contrib import admin

from .models import Student, StaffMember, Subject, Enrolment, School

admin.site.register(Student)
admin.site.register(StaffMember)
admin.site.register(Subject)
admin.site.register(Enrolment)
admin.site.register(School)
