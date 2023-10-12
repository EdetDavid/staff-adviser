from django.contrib import admin

from appointments.models import Admin, Student, Staff, StaffServiceField, Appointment, \
    ApprovedStudentAppointment, Chat, User, Post

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(StaffServiceField)
admin.site.register(Appointment)
admin.site.register(Chat)
#  admin.site.register(ApprovedCustomerAppointment)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Post, PostAdmin)
