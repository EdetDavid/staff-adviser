from django.contrib import admin

from appointments.models import Admin, Student, Staff, StaffServiceField, Appointment, \
    ApprovedStudentAppointment, Chat, User


admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(StaffServiceField)
admin.site.register(Appointment)
admin.site.register(Chat)
#  admin.site.register(ApprovedCustomerAppointment)
