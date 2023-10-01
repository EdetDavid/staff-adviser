from django import forms

from . import models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import datetime
from django.forms.widgets import SelectDateWidget
from django.utils import timezone

from .models import *

service_field = \
    [('Academics', 'Academics'),
     ('Career', 'Career'),
     ('Technology and Digital Literacy', 'Technology and Digital Literacy'),
     ('Mental Health and Wellness', 'Mental Health and Wellness')]  # field for staffs




class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'


# Admin registration form
class AdminRegistrationForm(UserCreationForm):  # to register an admin
    username = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your username'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email = forms.EmailField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your email'}))
    email.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    dob = forms.DateField(
        label="", widget=SelectDateWidget(years=range(1960, 2021)))
    dob.widget.attrs.update({'class': 'app-form-control-date'})

    address = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your address'}))
    address.widget.attrs.update({'class': 'app-form-control'})

    city = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'City'}))
    city.widget.attrs.update({'class': 'app-form-control'})

    country = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Country'}))
    country.widget.attrs.update({'class': 'app-form-control'})

    postcode = forms.IntegerField(
        label="", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    postcode.widget.attrs.update({'class': 'app-form-control'})

    image = forms.ImageField(label="")
    image.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'dob', 'address', 'city', 'country', 'postcode',
                  'image', 'password1', 'password2']
        help_texts = {k: "" for k in fields}


# Admin details update form
class AdminUpdateForm(forms.ModelForm):  # used to edit an admin instance
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    address = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    postcode = forms.IntegerField()
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Admin
        fields = ['first_name', 'last_name', 'dob',
                  'address', 'city', 'country', 'postcode', 'image']


# Admin appointment form
class AdminAppointmentForm(forms.ModelForm):  # book an appointment by admin
    # staff is chosen from existing staffs in db
    staff = forms.TypedChoiceField(label='')
    staff.widget.attrs.update({'class': 'app-form-control'})
    # student is chosen from existing student in db
    student = forms.TypedChoiceField(label='')
    student.widget.attrs.update({'class': 'app-form-control'})
    app_date = forms.DateField(label='', widget=SelectDateWidget(
        years=range(2022, 2024)))  # appointment date
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, *args, **kwargs):
        super(AdminAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['staff'].choices = [(c.id, c.first_name + " " + c.last_name + " (" + c.service_field + ")")
                                        for c in Staff.objects.filter(status=True).all()]
        # choose staffs from db

        self.fields['student'].choices = [(c.id, c.first_name + " " + c.last_name + " (" + c.department + ")")
                                          for c in Student.objects.filter(status=True).all()]
        # choose student from db
        self.fields['app_time'].choices = [('9:00 AM', '9:00 AM'), ('10:00 AM', '10:00 AM'), ('11:00 AM', '11:00 AM'),
                                           ('13:00 PM', '13:00 PM'), ('14:00 PM',
                                                                      '14:00 PM'), ('15:00 PM', '15:00 PM'),
                                           ('16:00 PM', '16:00 PM'), ('17:00 PM', '17:00 PM')]
        # choices for time slot for appointment

    class Meta:
        model = Appointment
        fields = ['description', 'app_date', 'app_time']


# student registration form
class StudentRegistrationForm(UserCreationForm):  # register student
    username = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your registration number'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email = forms.EmailField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your email'}))
    email.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    dob = forms.DateField(
        label="", widget=SelectDateWidget(years=range(1960, 2022)))
    dob.widget.attrs.update({'class': 'app-form-control-date'})

    department = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your department name'}))
    department.widget.attrs.update({'class': 'app-form-control'})

    address = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your  address'}))
    address.widget.attrs.update({'class': 'app-form-control'})

    city = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'City'}))
    city.widget.attrs.update({'class': 'app-form-control'})

    country = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Country'}))
    country.widget.attrs.update({'class': 'app-form-control'})

    postcode = forms.IntegerField(
        label="", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    postcode.widget.attrs.update({'class': 'app-form-control'})

    image = forms.ImageField(label="")
    image.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'dob', 'department', 'address',
                  'city', 'country', 'postcode', 'image', 'password1', 'password2']
        help_texts = {k: "" for k in fields}


# student update form
class StudentUpdateForm(forms.ModelForm):  # update student details
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    department = forms.CharField()
    address = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    postcode = forms.IntegerField()
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'dob', 'department', 'address', 'city', 'country', 'postcode',
                  'image']


# student appointment form
# make an appointment by student
class StudentAppointmentForm(forms.ModelForm):
    staff = forms.TypedChoiceField(label='')  # choose staff from db
    staff.widget.attrs.update({'class': 'app-form-control'})
    # staff_id=forms.CharField(widget=forms.Select(choices=c))
    app_date = forms.DateField(label='', widget=SelectDateWidget(
        years=range(2022, 2024)))  # date of appointment
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, *args, **kwargs):
        super(StudentAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['staff'].choices = [(e.id, e.first_name + " " + e.last_name + " (" + e.service_field + ")")
                                        for e in Staff.objects.filter(status=True).all()]
        # choose staff from db
        self.fields['app_time'].choices = [('9:00 AM', '9:00 AM'), ('10:00 AM', '10:00 AM'), ('11:00 AM', '11:00 AM'),
                                           ('13:00 PM', '13:00 PM'), ('14:00 PM',
                                                                      '14:00 PM'), ('15:00 PM', '15:00 PM'),
                                           ('16:00 PM', '16:00 PM'), ('17:00 PM', '17:00 PM')]
        # choices for time slot for appointment

    class Meta:
        model = Appointment
        fields = ['description', 'app_date', 'app_time']


# Staff registration form
class StaffRegistrationForm(UserCreationForm):  # register staff
    username = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your username'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email = forms.EmailField(required=True, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your email'}))
    email.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    dob = forms.DateField(
        label="", widget=SelectDateWidget(years=range(1960, 2021)))
    dob.widget.attrs.update({'class': 'app-form-control-date'})

    address = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your address'}))
    address.widget.attrs.update({'class': 'app-form-control'})

    city = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'City'}))
    city.widget.attrs.update({'class': 'app-form-control'})

    country = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Country'}))
    country.widget.attrs.update({'class': 'app-form-control'})

    postcode = forms.IntegerField(
        label="", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    postcode.widget.attrs.update({'class': 'app-form-control'})

    image = forms.ImageField(label="")
    image.widget.attrs.update({'class': 'app-form-control'})

    service_field = forms.CharField(
        label="", widget=forms.Select(choices=service_field))
    service_field.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'service_field', 'dob', 'address', 'city', 'country',
                  'postcode', 'image', 'password1', 'password2']
        help_texts = {k: "" for k in fields}

    def check_date(self):  # form date of birth validator
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        if dob < timezone.now().date():
            return True
        self.add_error('dob', 'Invalid date of birth.')
        return False


# staff update details form
class StaffUpdateForm(forms.ModelForm):  # update staff details
    first_name = forms.CharField()
    last_name = forms.CharField()
    # age = forms.IntegerField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    address = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    postcode = forms.IntegerField()
    image = forms.ImageField(widget=forms.FileInput)
    service_field = forms.CharField(
        label="", widget=forms.Select(choices=service_field))
    service_field.widget.attrs.update({'class': 'app-form-control'})

    # appfees = forms.FloatField()
    # admfees = forms.FloatField()

    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'dob', 'service_field',
                  'address', 'city', 'country', 'postcode', 'image']
        # 'appfees', 'admfees']


# Staff approve appointment form
# staff approves an appointment
class AppointmentApprovalForm(forms.ModelForm):
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'DESCRIPTION'}))
    description.widget.attrs.update({'class': 'app-form-control'})
    approval_date = forms.DateField(label='', widget=SelectDateWidget)
    approval_date.widget.attrs.update({'class': 'app-form-control-date'})

    class Meta:
        model = ApprovedStudentAppointment
        fields = ['description', 'approval_date']


# Staff edit appointment form
class AppointmentUpdateForm(forms.ModelForm):
    # staff can edit appointment description field, be it adding new lines or deleting a few of the old one
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'DESCRIPTION'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = Appointment
        fields = ['description']


# Feedback form
# contact us form (feedback), used by student/staff to send feedbacks using mail to admins
class FeedbackForm(forms.Form):
    APPOINTMENT = 'app'
    BUG = 'b'
    FEEDBACK = 'fb'
    NEW_FEATURE = 'nf'
    OTHER = 'o'
    subject_choices = (
        (APPOINTMENT, 'Appointment'),
        (FEEDBACK, 'Feedback'),
        (NEW_FEATURE, 'Feature Request'),
        (BUG, 'Bug'),
        (OTHER, 'Other'),
    )

    Name = forms.CharField(max_length=30, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your name'}))
    Name.widget.attrs.update({'class': 'form-control'})
    Email = forms.EmailField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'example@email.com'}))
    Email.widget.attrs.update({'class': 'form-control'})
    Subject = forms.ChoiceField(label='', choices=subject_choices)
    Subject.widget.attrs.update({'class': 'form-control'})
    Message = forms.CharField(max_length=500, label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter your message here'}))
    Message.widget.attrs.update({'class': 'form-control'})
