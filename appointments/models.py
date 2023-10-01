from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime




class User(AbstractUser):
    username = models.CharField(max_length=200, null=True, unique=True)
    email = models.EmailField(unique=True, null=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

service_field = \
    [('Academics', 'Academics'),
     ('Career', 'Career'),
     ('Technology and Digital Literacy', 'Technology and Digital Literacy'),
     ('Mental Health and Wellness', 'Mental Health and Wellness')]  # field for staffs


# Default user - deleted
def default_user():  # deleted users
    user = User(username="deleteduser", email="deleteduser@deleted.com")
    return user.id


# Admin
class Admin(models.Model):  # Admin details
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="Admin")  # user foreign key
    image = models.ImageField(default="default.png",
                              upload_to="profile_pictures")  # profile picture
    first_name = models.CharField(
        max_length=100, default='first_name')  # admin first name
    last_name = models.CharField(
        max_length=100, default='last_name')  # admin lastname
    dob = models.DateField(default=datetime.date.today)  # date of birth
    # contact?
    address = models.CharField(
        max_length=300, default="address")  # admin address
    city = models.CharField(max_length=100, default="city")  # admin city
    country = models.CharField(
        max_length=100, default="country")  # admin country
    postcode = models.IntegerField(default=0)  # admin postcode
    # admin status (approved/on-hold)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.admin.username} Admin Profile'


# Student
class Student(models.Model):  # student details
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="Student")  # user foreign key
    image = models.ImageField(default="default.png", upload_to="profile_pictures", null=True,
                              blank=True)  # profile picture
    first_name = models.CharField(
        max_length=100, default='first_name')  # student first name
    last_name = models.CharField(
        max_length=100, default='last_name')  # student last name
    # student date of birth
    dob = models.DateField(default=datetime.date.today)
    department = models.CharField(
        max_length=300, default="department")  # student address
    address = models.CharField(
        max_length=300, default="address")  # student address
    # contact?
    city = models.CharField(max_length=100, default="city")  # student city
    country = models.CharField(
        max_length=100, default="country")  # student country
    postcode = models.IntegerField(default=0)  # student postcode
    # student status (approved/on-hold)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.username} student Profile'




# Staff
class Staff(models.Model):  # staff details
    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="Staff")  # user foreign key
    image = models.ImageField(default="default.png",
                              upload_to="profile_pictures")  # profile picture
    first_name = models.CharField(
        max_length=100, default='first_name')  # staff firstname
    last_name = models.CharField(
        max_length=100, default='last_name')  # staff lastname
    # staff date of birth
    dob = models.DateField(default=datetime.date.today)
    address = models.CharField(
        max_length=300, default="address")  # staff address
    city = models.CharField(max_length=100, default="city")  # staff city
    country = models.CharField(
        max_length=100, default="country")  # staff country
    postcode = models.IntegerField(default=0)  # staff postcode
    service_field = models.CharField(max_length=50, choices=service_field,
                                     default='Service and Repair')  # staff service field from choices given as list
    # staff status(approved/on-hold)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.staff.username} Staff Profile'


# staff service field
class StaffServiceField(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="StaffServiceField")  # staff fk
    # total students/appointments completed by staff
    app_total = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.staff.first_name} Service Field Information'


# Appointment
class Appointment(models.Model):  # student appointment details
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="StudentApp")  # student fk
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="StaffApp")  # staff fk
    description = models.TextField(max_length=500)  # appointment description
    app_link = models.TextField(null=True, blank=True)  # video call room link
    app_date = models.DateField(null=True, blank=True)  # call date
    app_time = models.TextField(null=True, blank=True)
    # appointment status (approved/on-hold)
    status = models.BooleanField(default=False)
    # appointment completed/to-be-done
    completed = models.BooleanField(default=False)
    # approval_date = models.DateField(null=True, blank=True)  # date appointment approved
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.description} Appointment Information'


# Appointment rating
class AppointmentRating(models.Model):
    rating = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(0)])

    def __str__(self):
        return f'{self.rating} Stars - Appointment Rating Information'


# Approved appointment
class ApprovedStudentAppointment(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="StudentApprovedApp")  # student fk
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="StaffApprovedApp")  # staff fk
    approval_date = models.DateField()  # date appointment approved
    description = models.TextField()  # appointment description
    # date of completed appointment
    completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.student} Approved Appointment Information'




# Chatbot Model
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'