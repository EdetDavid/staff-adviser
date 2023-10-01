from .models import Chat
import openai
from django.http import JsonResponse
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail, mail_admins
from django.db.models.functions import TruncMonth
import datetime
from . import forms, models

from datetime import date, time
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from django.shortcuts import render, redirect
from xhtml2pdf import pisa

from appointments.forms import (
    AdminRegistrationForm,
    AdminUpdateForm,
    AdminAppointmentForm,
    StudentRegistrationForm,
    StudentUpdateForm,
    StudentAppointmentForm,
    StaffRegistrationForm,
    StaffUpdateForm,
    AppointmentUpdateForm,
    AppointmentApprovalForm,
)
from appointments.models import (
    User,
    Admin,
    Staff,
    Student,
    Appointment,
    StaffServiceField,
    ApprovedStudentAppointment,
    AppointmentRating,
)


# Home
def home_view(request):  # Homepage
    return render(request, "appointments/account/login.html")


# blog
def blog_view(request):  # Blogpage
    return render(request, "appointments/blog/blog.html")

# Account


def login_view(request):  # Login
    return render(request, "appointments/account/login.html")


# Admin
def register_adm_view(request):  # register admin
    if request.method == "POST":
        registration_form = AdminRegistrationForm(request.POST, request.FILES)
        if registration_form.is_valid():  # get data from form (if it is valid)
            dob = registration_form.cleaned_data.get(
                "dob"
            )  # get date of birth from form
            today = date.today()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )  # calculate age from dob
            if (
                dob < timezone.now().date()
            ):  # check if date of birth is valid (happened the previous day or even back)
                new_user = User.objects.create_user(
                    username=registration_form.cleaned_data.get("username"),
                    email=registration_form.cleaned_data.get("email"),
                    password=registration_form.cleaned_data.get("password1"),
                )  # create user
                adm = Admin(
                    admin=new_user,
                    first_name=registration_form.cleaned_data.get(
                        "first_name"),
                    last_name=registration_form.cleaned_data.get("last_name"),
                    # age=form.cleaned_data.get('age'),
                    dob=registration_form.cleaned_data.get("dob"),
                    address=registration_form.cleaned_data.get("address"),
                    city=registration_form.cleaned_data.get("city"),
                    country=registration_form.cleaned_data.get("country"),
                    postcode=registration_form.cleaned_data.get("postcode"),
                    image=request.FILES["image"],
                )  # create admin
                adm.save()
                group = Group.objects.get_or_create(
                    name="Admin"
                )  # add user to admin group
                group[0].user_set.add(new_user)

                messages.add_message(request, messages.INFO,
                                     "Registration successful!")
                return redirect("login_adm.html")
            else:
                registration_form.add_error("dob", "Invalid date of birth.")
        else:
            print(registration_form.errors)
            return render(
                request,
                "appointments/admin/register_adm.html",
                {"registration_form": registration_form},
            )
    else:
        registration_form = AdminRegistrationForm()

    return render(
        request,
        "appointments/admin/register_adm.html",
        {"registration_form": registration_form},
    )


# Login admin
def login_adm_view(request):  # login admin
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")  # get username
            password = login_form.cleaned_data.get("password")  # get password
            user = auth.authenticate(
                username=username, password=password
            )  # authenticate user
            # if user exists and is admin
            if user is not None and check_admin(user):
                auth.login(request, user)  # login user
                account_approval = Admin.objects.all().filter(
                    status=True, admin_id=request.user.id
                )  # if account is approved
                if account_approval:
                    return redirect("profile_adm.html")
                    # return redirect('dashboard_adm.html')
                else:  # if account is not yet approved
                    auth.logout(request)
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your account is currently pending. "
                        "Please wait for approval.",
                    )
                    return render(
                        request,
                        "appointments/admin/login_adm.html",
                        {"login_form": login_form},
                    )
        return render(
            request, "appointments/admin/login_adm.html", {
                "login_form": login_form}
        )
    else:
        login_form = AuthenticationForm()

    return render(
        request, "appointments/admin/login_adm.html", {
            "login_form": login_form}
    )


# Admin dashboard
@login_required(login_url="login_adm.html")
def dashboard_adm_view(request):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        adm_det = Admin.objects.all().filter(status=True)  # get all on-hold admins
        sta = Staff.objects.all().filter(status=True)  # get all on-hold staffs
        stu = Student.objects.all().filter(status=True)  # get all on-hold students
        app = Appointment.objects.all().filter(
            status=True
        )  # get all on-hold appointments

        adm_total = Admin.objects.all().count()  # total students
        stu_total = Student.objects.all().count()  # total students
        sta_total = Staff.objects.all().count()  # get total staffs
        app_total = Appointment.objects.all().count()  # get total appointments

        pending_adm_total = (
            Admin.objects.all().filter(status=False).count()
        )  # count onhold admins
        pending_stu_total = (
            Student.objects.all().filter(status=False).count()
        )  # get total onhold students
        pending_sta_total = (
            Staff.objects.all().filter(status=False).count()
        )  # get total onhold staffs
        pending_app_total = (
            Appointment.objects.all().filter(status=False).count()
        )  # get total onhold appointments

        messages.add_message(
            request,
            messages.INFO,
            "There are {0} appointments that require approval.".format(
                pending_app_total
            ),
        )

        context = {
            "adm": adm,
            "sta": sta,
            "stu": stu,
            "app": app,
            "adm_det": adm_det,
            "adm_total": adm_total,
            "stu_total": stu_total,
            "sta_total": sta_total,
            "app_total": app_total,
            "pending_adm_total": pending_adm_total,
            "pending_stu_total": pending_stu_total,
            "pending_sta_total": pending_sta_total,
            "pending_app_total": pending_app_total,
        }  # render information

        return render(request, "appointments/admin/dashboard_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Admin profile
@login_required(login_url="login_adm.html")
def profile_adm_view(request):
    if check_admin(request.user):
        # get information from database
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        dob = adm.dob
        today = date.today()
        age = today.year - dob.year - \
            ((today.month, today.day) < (dob.month, dob.day))
        if request.method == "POST":  # profile is updated
            admin_update_form = AdminUpdateForm(
                request.POST, request.FILES, instance=adm
            )
            if admin_update_form.is_valid():
                admin_update_form.save()  # save changes in profile

                messages.add_message(
                    request, messages.INFO, "Profile updated successfully!"
                )
                return redirect("profile_adm.html")
        else:
            admin_update_form = AdminUpdateForm(instance=adm)
        context = {  # render information on webpage
            "admin_update_form": admin_update_form,
            "adm": adm,
            "age": age,
        }
        return render(request, "appointments/admin/profile_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Admin book appointment
@login_required(login_url="login_adm.html")
def book_app_adm_view(request):  # book appointment
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        if request.method == "POST":  # if form is submitted
            app_form = AdminAppointmentForm(request.POST)
            if app_form.is_valid():
                sta_id = app_form.cleaned_data.get(
                    "staff")  # get staff id
                stu_id = app_form.cleaned_data.get(
                    "student")  # get student id

                sta = Staff.objects.all().filter(id=sta_id).first()  # get staff
                stu = Student.objects.all().filter(id=stu_id).first()  # get student

                if check_sta_availability(
                    sta,
                    app_form.cleaned_data.get("app_date"),
                    app_form.cleaned_data.get("app_time"),
                ):  # check if appointment is available during that slot
                    app = Appointment(
                        staff=sta,
                        student=stu,
                        description=app_form.cleaned_data.get("description"),
                        app_date=app_form.cleaned_data.get("app_date"),
                        app_time=app_form.cleaned_data.get("app_time"),
                        status=True,
                    )  # create new appointment
                    app.save()
                    messages.add_message(
                        request, messages.INFO, "Appointment created.")
                    return redirect("book_app_adm.html")
                else:  # if slot is not available, display error
                    messages.add_message(
                        request, messages.INFO, "Time slot unavailable."
                    )
                    return render(
                        request,
                        "appointments/admin/book_app_adm.html",
                        {"app_form": app_form},
                    )
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    "Error creating an appointment. Please try again.",
                )
                print(app_form.errors)
        else:
            app_form = AdminAppointmentForm()
        return render(
            request,
            "appointments/admin/book_app_adm.html",
            {"adm": adm, "app_form": app_form},
        )
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Admin download summary report
def dl_report_adm_action(request):
    template_path = "appointments/admin/summary_report.html"
    admin = Admin.objects.filter(admin_id=request.user.id).first()
    admin_details = Admin.objects.filter(status=True).all()
    staff_on_hold = Staff.objects.filter(status=True).all()
    students_on_hold = Student.objects.filter(status=True).all()
    appointments_on_hold = Appointment.objects.filter(status=True).all()

    admin_total = Admin.objects.count()
    student_total = Student.objects.count()
    staff_total = Staff.objects.count()
    appointment_total = Appointment.objects.count()

    pending_admin_total = Admin.objects.filter(status=True).count()
    pending_student_total = Student.objects.filter(status=True).count()
    pending_staff_total = Staff.objects.filter(status=True).count()
    pending_appointment_total = Appointment.objects.filter(
        status=True).count()

    context = {
        "admin": admin,
        "staff": staff_on_hold,
        "students": students_on_hold,
        "appointments": appointments_on_hold,
        "admin_details": admin_details,
        "admin_total": admin_total,
        "student_total": student_total,
        "staff_total": staff_total,
        "appointment_total": appointment_total,
        "pending_admin_total": pending_admin_total,
        "pending_student_total": pending_student_total,
        "pending_staff_total": pending_staff_total,
        "pending_appointment_total": pending_appointment_total,
    }

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="staff-adviser_summary-report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response

# Admin approve appointment


@login_required(login_url="login_adm.html")
def approve_app_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        appointment = Appointment.objects.get(id=pk)
        appointment.status = True  # approve appointment
        appointment.save()

        messages.success(request, "Appointment approved successfully.")
        return redirect(reverse("view_all_app_adm.html"))
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# All appointments: pending, incomplete, completed
@login_required(login_url="login_adm.html")
def all_app_adm_view(request):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        app = Appointment.objects.all().filter(status=True)
        appointment_app = Appointment.objects.all().filter(status=True).count()
        app_count = Appointment.objects.all().count()
        pending_app_total = Appointment.objects.all().filter(status=False).count()
        approved_app_total = Appointment.objects.all().filter(status=True).count()

        appointment_details = []
        # get approved appointments
        for app in Appointment.objects.filter(status=True).all():
            e = app.staff
            c = app.student
            if e and c:
                appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.pk,
                        app.completed,
                        app.status,
                    ]
                )  # render information

        pending_appointment_details = []
        # get pending appointments
        for app in Appointment.objects.filter(status=False).all():
            e = app.staff
            c = app.student
            if e and c:
                pending_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.id,
                        app.completed,
                        app.status,
                    ]
                )  # render information on webpage

        return render(
            request,
            "appointments/admin/view_all_app_adm.html",
            {
                "adm": adm,
                "app": app,
                "appointment_app": appointment_app,
                "app_count": app_count,
                "pending_app_total": pending_app_total,
                "approved_app_total": approved_app_total,
                "appointment_details": appointment_details,
                "pending_appointment_details": pending_appointment_details,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Admin appointment view
@login_required(login_url="login_adm.html")
def appointment_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        app = Appointment.objects.all().filter(status=False)
        appointment_app = Appointment.objects.all().filter(status=True).count()
        app_count = Appointment.objects.all().count()
        pending_app_total = Appointment.objects.all().filter(status=False).count()
        approved_app_total = Appointment.objects.all().filter(status=True).count()
        context = {
            "adm": adm,
            "app": app,
            "appointment_app": appointment_app,
            "app_count": app_count,
            "pending_app_total": pending_app_total,
            "approved_app_total": approved_app_total,
        }
        return render(request, "appointments/admin/appointment_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approved appointment's details
@login_required(login_url="login_adm.html")
def app_details_adm_view(request, pk):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()

        app = Appointment.objects.filter(id=pk).first()  # get appointment
        sta = app.staff
        stu = app.student

        app.app_link = stu.first_name

        appointment_details = [
            sta.first_name,
            sta.last_name,
            sta.service_field,
            stu.first_name,
            stu.last_name,
            stu.department,
            stu.address,
            stu.postcode,
            stu.city,
            stu.country,
            app.app_date,
            app.app_time,
            app.app_link,
            app.description,
            app.status,
            app.completed,
            pk,
        ]  # render fields

        return render(
            request,
            "appointments/admin/view_app_details_adm.html",
            {
                "adm": adm,
                "sta": sta,
                "app": app,
                "stu": stu,
                "appointment_details": appointment_details,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Complete appointment action
@login_required(login_url="login_adm.html")
def complete_app_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database and render in html webpage
        app = Appointment.objects.get(id=pk)
        app.completed = True
        app.save()

        messages.add_message(
            request, messages.INFO, "Appointment completed successfully!"
        )
        return redirect("view_all_app_adm.html")
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Statistics page
@login_required(login_url="login_adm.html")
def statistics_adm_view(request):
    if check_admin(request.user):
        sta = Staff.objects.all().filter(status=False)  # get all on-hold staffs
        stu = Student.objects.all().filter(status=False)  # get all on-hold students

        stu_total = Student.objects.all().count()  # total students
        sta_total = Staff.objects.all().count()  # get total staffs
        app_total = Appointment.objects.all().count()  # get total appointments

        pending_stu_total = (
            Student.objects.all().filter(status=False).count()
        )  # get total onhold students
        pending_sta_total = (
            Staff.objects.all().filter(status=False).count()
        )  # get total onhold staffs
        pending_app_total = (
            Appointment.objects.all().filter(status=False).count()
        )  # get total onhold appointments

        context = {
            "sta": sta,
            "stu": stu,
            "stu_total": stu_total,
            "sta_total": sta_total,
            "app_total": app_total,
            "pending_stu_total": pending_stu_total,
            "pending_sta_total": pending_sta_total,
            "pending_app_total": pending_app_total,
        }  # render information

        return render(request, "appointments/admin/view_statistics_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# View statistics (pivot data)
@login_required(login_url="login_adm.html")
def pivot_data(request):
    dataset = Appointment.objects.all()
    data = serializers.serialize("json", dataset)
    return JsonResponse(data, safe=False)


# Student section
@login_required(login_url="login_adm.html")
def student_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        stu = Student.objects.all().filter(status=False)
        stu_approved = Student.objects.all().filter(status=True).count()
        stu_pending = Student.objects.all().filter(status=False).count()
        stu_count = Student.objects.all().count()
        context = {
            "adm": adm,
            "stu": stu,
            "stu_pending": stu_pending,
            "stu_approved": stu_approved,
            "stu_count": stu_count,
        }
        return render(request, "appointments/admin/student_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approve student account
@login_required(login_url="login_adm.html")
def approve_stu_adm_view(request):  # Approve student
    # get information from database and render in html webpage
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        stu = Student.objects.all().filter(status=False)
        stu_approved = Student.objects.all().filter(status=True).count()
        stu_pending = Student.objects.all().filter(status=False).count()
        stu_count = Student.objects.all().count()

        context = {
            "adm": adm,
            "stu": stu,
            "stu_pending": stu_pending,
            "stu_approved": stu_approved,
            "stu_count": stu_count,
        }

        return render(request, "appointments/admin/approve_stu.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approve student action
@login_required(login_url="login_adm.html")
def approve_stu_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        stu = Student.objects.get(id=pk)
        stu.status = True  # approve student
        stu.save()

        messages.add_message(request, messages.INFO,
                             "Student approved successfully.")
        return redirect(reverse("approve_stu.html"))
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# View all students
@login_required(login_url="login_adm.html")
def all_stu_adm_view(request):  # View all students
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        stu = Student.objects.all().filter(status=True)
        stu_approved = Student.objects.all().filter(status=True).count()
        stu_pending = Student.objects.all().filter(status=False).count()
        stu_count = Student.objects.all().count()
        stu_details = []

        for c in Student.objects.filter(status=True).all():
            stu_details.append(
                [
                    c.id,
                    c.image.url,
                    c.first_name,
                    c.last_name,
                    c.student.username,
                    c.department,
                    c.postcode,
                    c.city,
                    c.country,
                    c.status,
                ]
            )

        context = {
            "adm": adm,
            "stu": stu,
            "stu_pending": stu_pending,
            "stu_approved": stu_approved,
            "stu_count": stu_count,
            "stu_details": stu_details,
        }

        return render(request, "appointments/admin/view_all_stu.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Staffs section
@login_required(login_url="login_adm.html")
def staff_adm_view(request):  # view staffs
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        sta = Staff.objects.all().filter(status=False)
        sta_approved = Staff.objects.all().filter(status=True).count()
        sta_pending = Staff.objects.all().filter(status=False).count()
        sta_count = Staff.objects.all().count()
        context = {
            "adm": adm,
            "sta": sta,
            "sta_approved": sta_approved,
            "sta_pending": sta_pending,
            "sta_count": sta_count,
        }
        return render(request, "appointments/admin/staff_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approved staff account
@login_required(login_url="login_adm.html")
def approve_sta_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        sta = Staff.objects.all().filter(status=False)
        sta_approved = Staff.objects.all().filter(status=True).count()
        sta_pending = Staff.objects.all().filter(status=False).count()
        sta_count = Staff.objects.all().count()
        context = {
            "adm": adm,
            "sta": sta,
            "sta_approved": sta_approved,
            "sta_pending": sta_pending,
            "sta_count": sta_count,
        }
        return render(request, "appointments/admin/approve_sta.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approve staff action
@login_required(login_url="login_adm.html")
def approve_sta_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        sta = Staff.objects.get(id=pk)
        sta.status = True  # approve staff
        sta.save()

        messages.add_message(request, messages.INFO,
                             "Staff approved successfully.")
        return redirect(reverse("approve_sta.html"))
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# View all staff
@login_required(login_url="login_adm.html")
def all_sta_adm_view(request):
    # get information from database and render in html webpage
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        sta = Staff.objects.all().filter(status=False)
        sta_approved = Staff.objects.all().filter(status=True).count()
        sta_pending = Staff.objects.all().filter(status=False).count()
        sta_count = Staff.objects.all().count()

        sta_details = []
        for e in Staff.objects.filter(status=True).all():
            esf = StaffServiceField.objects.filter(staff=e).first()
            sta_details.append(
                [
                    e.id,
                    e.image.url,
                    e.first_name,
                    e.last_name,
                    e.dob,
                    e.address,
                    e.postcode,
                    e.city,
                    e.country,
                    e.service_field,
                    e.status,
                    
                ]
            )

        context = {
            "adm": adm,
            "sta": sta,
            "sta_approved": sta_approved,
            "sta_pending": sta_pending,
            "sta_count": sta_count,
            "sta_details": sta_details,
        }

        return render(request, "appointments/admin/view_all_sta.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# View admin
@login_required(login_url="login_adm.html")
def admin_adm_view(request):
    # get information from database and render in html webpage
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        adm_details = Admin.objects.all().filter()
        adm_approved = Admin.objects.all().filter(status=True).count()
        adm_pending = Admin.objects.all().filter(status=False).count()
        adm_count = Admin.objects.all().count()
        context = {
            "adm": adm,
            "adm_details": adm_details,
            "adm_approved": adm_approved,
            "adm_pending": adm_pending,
            "adm_count": adm_count,
        }
        return render(request, "appointments/admin/admin_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approve admin account
@login_required(login_url="login_adm.html")
def approve_adm_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        adm_details = Admin.objects.all().filter(status=False)
        adm_approved = Admin.objects.all().filter(status=True).count()
        adm_pending = Admin.objects.all().filter(status=False).count()
        adm_count = Admin.objects.all().count()
        context = {
            "adm": adm,
            "adm_details": adm_details,
            "adm_approved": adm_approved,
            "adm_pending": adm_pending,
            "adm_count": adm_count,
        }

        return render(request, "appointments/admin/approve_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Approve admin action
@login_required(login_url="login_adm.html")
def approve_adm_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        adm = Admin.objects.get(id=pk)
        adm.status = True  # approve admin
        adm.save()
        messages.add_message(request, messages.INFO,
                             "Admin approved successfully.")
        return redirect(reverse("approve_adm.html"))
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# View all admins
@login_required(login_url="login_adm.html")
def all_adm_adm_view(request):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        adm_approved = Admin.objects.all().filter(status=True).count()
        adm_pending = Admin.objects.all().filter(status=False).count()
        adm_count = Admin.objects.all().count()

        # get information from database and render in html webpage
        adm_details = []
        for a in Admin.objects.all():
            adm_details.append(
                [
                    a.id,
                    a.image.url,
                    a.first_name,
                    a.last_name,
                    a.dob,
                    a.address,
                    a.city,
                    a.country,
                    a.postcode,
                    a.status,
                ]
            )

        context = {
            "adm": adm,
            "adm_approved": adm_approved,
            "adm_pending": adm_pending,
            "adm_count": adm_count,
            "adm_details": adm_details,
        }

        return render(request, "appointments/admin/view_all_adm.html", context)
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# S
def register_stu_view(request):  # Register student
    if request.method == "POST":
        registration_form = StudentRegistrationForm(
            request.POST, request.FILES)
        if registration_form.is_valid():  # if form is valid
            dob = registration_form.cleaned_data.get(
                "dob"
            )  # get date of birth from form
            if dob < timezone.now().date():  # check if date is valid
                new_user = User.objects.create_user(
                    username=registration_form.cleaned_data.get("username"),
                    email=registration_form.cleaned_data.get("email"),
                    password=registration_form.cleaned_data.get("password1"),
                )  # create use
                c = Student(
                    student=new_user,
                    first_name=registration_form.cleaned_data.get(
                        "first_name"),
                    last_name=registration_form.cleaned_data.get("last_name"),
                    dob=registration_form.cleaned_data.get("dob"),
                    department=registration_form.cleaned_data.get(
                        "department"),
                    address=registration_form.cleaned_data.get(
                        "address"
                    ),
                    city=registration_form.cleaned_data.get("city"),
                    country=registration_form.cleaned_data.get("country"),
                    postcode=registration_form.cleaned_data.get("postcode"),
                    image=request.FILES["image"],
                )  # create student
                c.save()

                group = Group.objects.get_or_create(
                    name="Student"
                )  # add user to patient group
                group[0].user_set.add(new_user)

                messages.add_message(request, messages.INFO,
                                     "Registration successful!")
                return redirect("login_stu.html")
            else:  # if date of birth is invalid
                registration_form.add_error("dob", "Invalid date of birth.")
                return render(
                    request,
                    "appointments/student/register_stu.html",
                    {"registration_form": registration_form},
                )
        else:
            print(registration_form.errors)
    else:
        registration_form = StudentRegistrationForm()
    return render(
        request,
        "appointments/student/register_stu.html",
        {"registration_form": registration_form},
    )


# Login student
def login_stu_view(request):  # Login student
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():  # if form is valid
            username = login_form.cleaned_data.get(
                "username")  # get username from form
            password = login_form.cleaned_data.get(
                "password")  # get password from form
            user = auth.authenticate(
                username=username, password=password)  # get user
            # if user exists and is a student
            if user is not None and check_student(user):
                auth.login(request, user)  # login
                account_approval = Student.objects.all().filter(
                    status=True, student_id=request.user.id
                )
                if account_approval:  # if account is approved
                    return redirect("profile_stu.html")
                else:  # if not approved, redirect to wait_approval webpage
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your account is currently pending. "
                        "Please wait for approval.",
                    )
                    return render(
                        request,
                        "appointments/student/login_stu.html",
                        {"login_form": login_form},
                    )
            elif ( user is None): # if user does not exits
                  messages.add_message(
                        request,
                        messages.ERROR,
                        "User does not exits or Invalid Details "
                    )
                      
        return render(
            request, "appointments/student/login_stu.html", {
                "login_form": login_form}
        )
    else:
        login_form = AuthenticationForm()

    return render(
        request, "appointments/student/login_stu.html", {
            "login_form": login_form}
    )


# Student profile
@login_required(login_url="login_stu.html")
def profile_stu_view(request):
    if check_student(request.user):
        # get information from database and render in html webpage
        stu = Student.objects.filter(student_id=request.user.id).first()
        dob = stu.dob
        today = date.today()
        age = (
            today.year - dob.year -
            ((today.month, today.day) < (dob.month, dob.day))
        )  # calculate age
        if request.method == "POST":
            student_update_form = StudentUpdateForm(
                request.POST, request.FILES, instance=stu
            )
            if student_update_form.is_valid():  # if form is valid
                dob = student_update_form.cleaned_data.get(
                    "dob"
                )  # get date of birth from form
                today = date.today()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )
                if dob < timezone.now().date():  # if date of birth is valid
                    student_update_form.save()  # save details
                    stu.age = stu  # save age
                    stu.save()

                    messages.add_message(
                        request, messages.INFO, "Profile updated successfully!"
                    )
                    return redirect("profile_stu.html")
                else:
                    student_update_form.add_error(
                        "dob", "Invalid date of birth.")
                    context = {
                        "student_update_form": student_update_form,
                        "stu": stu,
                        "age": age,
                        
                    }
                    return render(
                        request, "appointments/student/profile_stu.html", context
                    )
            else:
                print(student_update_form.errors)
        student_update_form = StudentUpdateForm(instance=stu)
        context = {
            "student_update_form": student_update_form,
            "stu": stu,
            "age": age,
        }
        return render(request, "appointments/student/profile_stu.html", context)
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# Student book appointment
@login_required(login_url="login_stu.html")
def book_app_stu_view(request):
    if check_student(request.user):
        stu = Student.objects.filter(student_id=request.user.id).first()
        app_details = []

        for app in Appointment.objects.filter(student=stu, status=True).all():
            e = app.staff
            if e:
                app_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.status,
                    ]
                )

        if request.method == "POST":  # if student books an appointment
            app_form = StudentAppointmentForm(request.POST)

            if app_form.is_valid():  # if form is valid
                # get staff id from form
                sta_id = int(app_form.cleaned_data.get("staff"))
                sta = (
                    Staff.objects.all().filter(id=sta_id).first()
                )  # get staff from form

                if check_sta_availability(
                    sta,  # check if staff is available during that slot
                    app_form.cleaned_data.get("app_date"),
                    app_form.cleaned_data.get("app_time"),
                ):
                    app_date = app_form.cleaned_data.get(
                        "app_date"
                    )  # get appointment date
                    if (
                        timezone.now().date() < app_date
                    ):  # check if appointment date is valid
                        app = Appointment(
                            staff=sta,
                            student=stu,
                            description=app_form.cleaned_data.get(
                                "description"),
                            app_date=app_form.cleaned_data.get("app_date"),
                            app_time=app_form.cleaned_data.get("app_time"),
                            status=False,
                        )  # create appointment instance, which is unapproved
                        app.save()
                        messages.add_message(
                            request,
                            messages.INFO,
                            "Your appointment is received and pending.",
                        )
                        return redirect("book_app_stu.html")
                    else:
                        app_form.add_error("app_date", "Invalid date.")
                else:  # if staff is busy
                    app_form.add_error("app_time", "Slot Unavailable.")
                return render(
                    request,
                    "appointments/student/book_app_stu.html",
                    {"app_form": app_form, "app_details": app_details},
                )
            else:  # if form is invalid
                print(app_form.errors)
        else:
            app_form = StudentAppointmentForm()
        return render(
            request,
            "appointments/student/book_app_stu.html",
            {"stu": stu, "app_form": app_form, "app_details": app_details},
        )
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# View student appointment dashboard
@login_required(login_url="login_stu.html")
def app_stu_view(request):
    if check_student(request.user):
        # get information from database and render in html webpage
        stu = Student.objects.filter(student_id=request.user.id).first()

        total_app = Appointment.objects.filter(student=stu).count()
        total_approved_app = Appointment.objects.filter(
            status=True, student=stu
        ).count()
        total_pending_app = Appointment.objects.filter(
            status=False, student=stu
        ).count()
        # app_total = Appointment.objects.filter(status=False, student=stu).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(
            status=False, completed=False, student=stu
        ).all():  # get all approved appointments
            e = app.staff
            c = app.student
            if e and c:
                pending_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(
            status=True, completed=False, student=stu
        ).all():  # get all approved appointments
            e = app.staff
            c = app.student
            if e and c:
                incomplete_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        appointment_details = []
        # get all approved appointments
        for app in Appointment.objects.filter(status=True, student=stu).all():
            e = app.staff
            c = app.student
            if e and c:
                appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        messages.add_message(
            request,
            messages.INFO,
            "You have {0} pending appointments.".format(total_pending_app),
        )

        context = {
            "stu": stu,
            "total_app": total_app,
            "total_approved_app": total_approved_app,
            "total_pending_app": total_pending_app,
            "pending_appointment_details": pending_appointment_details,
            "appointment_details": appointment_details,
            "incomplete_appointment_details": incomplete_appointment_details,
            # 'message': message
        }

        return render(request, "appointments/student/view_app_stu.html", context)
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# View all student appointments
@login_required(login_url="login_stu.html")
def all_app_stu_view(request):
    if check_student(request.user):
        # get information from database and render in html webpage
        stu = Student.objects.filter(student_id=request.user.id).first()

        total_app = Appointment.objects.filter(student=stu).count()
        total_approved_app = Appointment.objects.filter(
            status=True, student=stu
        ).count()
        total_pending_app = Appointment.objects.filter(
            status=False, student=stu
        ).count()
        # app_total = Appointment.objects.filter(status=False, student=stu).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(
            status=False, completed=False, student=stu
        ).all():  # get all approved appointments
            e = app.staff
            c = app.student
            if e and c:
                pending_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(
            status=True, completed=False, student=stu
        ).all():  # get all approved appointments
            e = app.staff
            c = app.student
            if e and c:
                incomplete_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        completed_appointment_details = []
        for app in Appointment.objects.filter(
            status=True, completed=True, student=stu
        ).all():  # get all approved appointments
            e = app.staff
            c = app.student
            if e and c:
                completed_appointment_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        c.first_name,
                        c.last_name,
                        app.pk,
                        app.description,
                        app.app_date,
                        app.app_time,
                        app.app_link,
                        app.status,
                        app.completed,
                        app.rating,
                    ]
                )

        messages.add_message(
            request,
            messages.INFO,
            "You have {0} appointments.".format(total_approved_app),
        )

        context = {
            "stu": stu,
            "total_app": total_app,
            "total_approved_app": total_approved_app,
            "total_pending_app": total_pending_app,
            "pending_appointment_details": pending_appointment_details,
            "completed_appointment_details": completed_appointment_details,
            "incomplete_appointment_details": incomplete_appointment_details,
        }

        return render(request, "appointments/student/view_all_app_stu.html", context)
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# Appointment rating
@login_required(login_url="login_stu.html")
# View approved appointment's details
@login_required(login_url="login_stu.html")
def app_details_stu_view(request, pk):
    if check_student(request.user):
        app = Appointment.objects.filter(id=pk).first()  # get appointment
        sta = app.staff
        stu = app.student

        app.app_link = stu.first_name

        appointment_details = [
            sta.first_name,
            sta.last_name,
            sta.service_field,
            stu.first_name,
            stu.last_name,
            stu.department,
            stu.address,
            stu.postcode,
            stu.city,
            stu.country,
            app.app_date,
            app.app_time,
            app.app_link,
            app.description,
            app.status,
            app.completed,
            pk,
        ]  # render fields
        return render(
            request,
            "appointments/student/view_app_details_stu.html",
            {
                "sta": sta,
                "app": app,
                "stu": stu,
                "appointment_details": appointment_details,
            },
        )

        # 'med': med})
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# Join meeting
@login_required(login_url="login_stu.html")
def join_meeting_stu_view(request):
    if check_student(request.user):
        # get information from database and render in html webpage
        stu = Student.objects.get(student_id=request.user.id)
        total_app = Appointment.objects.filter(student=stu).count()
        total_approved_app = Appointment.objects.filter(
            status=True, student=stu
        ).count()
        total_pending_app = Appointment.objects.filter(
            status=False, student=stu
        ).count()

        app_details = []
        for app in Appointment.objects.filter(
            status=True, student=stu, app_link__isnull=True
        ).all():  # get all approved appointments with room name
            e = app.staff
            if e:
                app.app_link = stu.first_name
                app_details.append(
                    [
                        app.pk,
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.app_link,
                        app.status,
                    ]
                )

        sta_details = []
        for (
            esf
        ) in (
            StaffServiceField.objects.all()
        ):  # get all staff service field instances
            e = esf.staff
            dob = e.dob
            today = date.today()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            if e.status:
                sta_details.append(
                    [
                        e.first_name,
                        e.last_name,
                        e.service_field,
                        e.city,
                        age,
                        esf.app_total,
                    ]
                )

        return render(
            request,
            "appointments/student/join_meeting_stu.html",
            {
                "stu": stu,
                "total_app": total_app,
                "total_approved_app": total_approved_app,
                "total_pending_app": total_pending_app,
                "app_details": app_details,
                "sta_details": sta_details,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# Appointment report
@login_required(login_url="login_stu.html")
def app_report_stu_view(request, pk):
    # get information from database and render in html webpage
    app = Appointment.objects.all().filter(id=pk).first()
    stu = app.student
    sta = app.doctor
    app_date = app.calldate
    app_time = app.calltime

    app_details = []

    context = {
        "stu_name": stu.first_name,
        "sta_name": sta.first_name,
        "app_date": app_date,
        "app_time": app_time,
        "app_desc": app.description,
        "stu_comp_name": app.department,
        "stu_comp_add": app.address,
        "app_details": app_details,
        "pk": pk,
    }

    if check_student(request.user):
        return render(request, "appointments/student/app_report_stu.html", context)
    # elif check_staff(request.user):
    #     return render(request, 'hospital/Doctor/report_apt.html', context)
    # elif check_admin(request.user):
    #     return render(request, 'hospital/Admin/report_apt.html', context)
    else:
        return render(request, "appointments/account/login.html")


# Student feedback
@login_required(login_url="login_stu.html")
def feedback_stu_view(request):
    if check_student(request.user):
        stu = Student.objects.get(student_id=request.user.id)
        feedback_form = forms.FeedbackForm()
        if request.method == "POST":
            feedback_form = forms.FeedbackForm(request.POST)
            if feedback_form.is_valid():  # if form is valid
                # get email from form
                email = feedback_form.cleaned_data["Email"]
                name = feedback_form.cleaned_data["Name"]  # get name from form
                subject = "You have a new Feedback from {}:<{}>".format(
                    name, feedback_form.cleaned_data["Email"]
                )  # get subject from form
                # get message from form
                message = feedback_form.cleaned_data["Message"]

                message = (
                    "Subject: {}\n"
                    "Date: {}\n"
                    "Message:\n\n {}".format(
                        dict(feedback_form.subject_choices).get(
                            feedback_form.cleaned_data["Subject"]
                        ),
                        datetime.datetime.now(),
                        feedback_form.cleaned_data["Message"],
                    )
                )

                try:
                    mail_admins(subject, message)
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Thank you for submitting your feedback.",
                    )

                    return redirect("feedback_stu.html")
                except:
                    feedback_form.add_error("Email", "Try again.")
                    return render(
                        request,
                        "appointments/student/feedback_stu.html",
                        {
                            "email": email,
                            "name": name,
                            "subject": subject,
                            "message": message,
                            "feedback_form": feedback_form,
                            "stu": stu,
                        },
                    )
        return render(
            request,
            "appointments/student/feedback_stu.html",
            {"feedback_form": feedback_form, "stu": stu},
        )
    else:
        auth.logout(request)
        return redirect("login_stu.html")


# Download report
def dl_app_report_action(request, pk):
    # get information from database
    template_path = "appointments/report/app_report_pdf.html"

    app = Appointment.objects.all().filter(id=pk).first()

    stu = app.student
    sta = app.staff

    app_date = app.app_date
    app_time = app.app_time

    app_details = []

    context = {
        "stu_name": stu.first_name,
        "sta_name": sta.first_name,
        "app_date": app_date,
        "app_time": app_time,
        "app_desc": app.description,
        "stu_comp_name": app.department,
        "stu_comp_add": app.address,
        "app_details": app_details,
    }
    # context = {'myvar': 'this is your templates context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="appointment_report.pdf"'
    # find the templates and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


# Staff
def register_sta_view(request):  # Register staff
    if request.method == "POST":
        registration_form = StaffRegistrationForm(
            request.POST, request.FILES)
        if registration_form.is_valid():  # if form is valid
            dob = registration_form.cleaned_data.get(
                "dob"
            )  # get date of birth from form
            if dob < timezone.now().date():  # if date of birth is valid
                new_user = User.objects.create_user(
                    username=registration_form.cleaned_data.get("username"),
                    email=registration_form.cleaned_data.get("email"),
                    password=registration_form.cleaned_data.get("password1"),
                )  # create new user
                sta = Staff(
                    staff=new_user,
                    first_name=registration_form.cleaned_data.get(
                        "first_name"),
                    last_name=registration_form.cleaned_data.get("last_name"),
                    service_field=registration_form.cleaned_data.get(
                        "service_field"),
                    dob=registration_form.cleaned_data.get("dob"),
                    address=registration_form.cleaned_data.get("address"),
                    city=registration_form.cleaned_data.get("city"),
                    country=registration_form.cleaned_data.get("country"),
                    postcode=registration_form.cleaned_data.get("postcode"),
                    image=request.FILES["image"],
                )  # create new staff
                sta.save()

                # appfees=200, admfees=2000)
                esf = StaffServiceField(staff=sta)
                esf.save()

                group = Group.objects.get_or_create(
                    name="Staff"
                )  # add user to doctor group
                group[0].user_set.add(new_user)

                messages.add_message(request, messages.INFO,
                                     "Registration successful!")
                return redirect("login_sta.html")
            else:  # if date of birth is invalid
                registration_form.add_error("dob", "Invalid date of birth.")
                return render(
                    request,
                    "appointments/staff/register_sta.html",
                    {"registration_form": registration_form},
                )
        else:
            print(registration_form.errors)
    else:
        registration_form = StaffRegistrationForm()

    return render(
        request,
        "appointments/staff/register_sta.html",
        {"registration_form": registration_form},
    )


# Login staff
def login_sta_view(request):
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)
            if user is not None and check_staff(user):
                auth.login(request, user)
                account_approval = Staff.objects.all().filter(
                    status=True, staff_id=request.user.id
                )
                if account_approval:
                    return redirect("profile_sta.html")
                else:
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your account is currently pending. "
                        "Please wait for approval.",
                    )
                    return render(
                        request,
                        "appointments/staff/login_sta.html",
                        {"login_form": login_form},
                    )
        return render(
            request, "appointments/staff/login_sta.html", {
                "login_form": login_form}
        )
    else:
        login_form = AuthenticationForm()
    return render(
        request, "appointments/staff/login_sta.html", {
            "login_form": login_form}
    )


# Staff profile
@login_required(login_url="login_sta.html")
def profile_sta_view(request):
    if check_staff(request.user):
        # get information from database and render in html webpage
        sta = Staff.objects.filter(staff_id=request.user.id).first()
        dob = sta.dob
        today = date.today()
        age = (
            today.year - dob.year -
            ((today.month, today.day) < (dob.month, dob.day))
        )  # calculate age
        if request.method == "POST":
            staff_update_form = StaffUpdateForm(
                request.POST, request.FILES, instance=sta
            )
            if staff_update_form.is_valid():  # if form is valid
                dob = staff_update_form.cleaned_data.get("dob")
                today = date.today()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )  # calculate age
                if dob < timezone.now().date():  # if date of birth is valid
                    staff_update_form.save()
                    esf = (
                        StaffServiceField.objects.all().filter(staff=sta).first()
                    )  # get doctor professional details
                    # dp.appfees = p_form.cleaned_data.get('appfees')
                    # dp.admfees = p_form.cleaned_data.get('admfees')
                    esf.save()  # save staff service field data

                    messages.add_message(
                        request, messages.INFO, "Profile updated successfully!"
                    )
                    return redirect("profile_sta.html")
                else:
                    staff_update_form.add_error(
                        "dob", "Invalid date of birth.")
                    context = {
                        "staff_update_form": staff_update_form,
                        "sta": sta,
                        "age": age,
                    }
                    return render(
                        request, "appointments/staff/profile_sta.html", context
                    )
        else:
            # get data from database and put initial values in form
            # age.refresh_from_db()
            esf = StaffServiceField.objects.all().filter(staff=sta).first()
            staff_update_form = StaffUpdateForm(instance=sta)
            # staff_update_form.fields['appfees'].initial = dp.appfees
            # staff_update_form.fields['admfees'].initial = dp.admfees
            context = {
                "staff_update_form": staff_update_form,
                "sta": sta,
                "age": age,
            }
            return render(request, "appointments/staff/profile_sta.html", context)
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# staff dashboard - approved appointments don't show, WHAT IS WRONG?!
@login_required(login_url="login_sta.html")
def dashboard_sta_view(request):
    if check_staff(request.user):
        # get information from database and render in html webpage
        sta = Staff.objects.get(staff_id=request.user.id)
        app_completed = (
            Appointment.objects.all().filter(staff=sta, completed=True).count()
        )
        available_app = (
            Appointment.objects.all().filter(staff=sta, status=False).count()
        )
        pending_app_count = (
            Appointment.objects.all().filter(staff=sta, status=False).count()
        )
        app_count = (
            models.Appointment.objects.all().filter(status=True, staff=sta).count()
        )

        pending_app = []
        for app in Appointment.objects.filter(
            status=False, staff=sta.id, app_link__isnull=True, completed=False
        ).all():  # get unapproved appointments which have links not set and are not yet finished
            c = Student.objects.filter(id=app.student.id).first()
            if c:
                pending_app.append(
                    [
                        app.pk,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.status,
                        app.completed,
                    ]
                )

        upcoming_app = []
        for app in Appointment.objects.filter(
            status=True, staff=sta.id, app_link__isnull=True, completed=False
        ).all():  # get approved appointments which have links not set and are not yet finished
            c = Student.objects.filter(id=app.student.id).first()
            app.app_link = c.first_name
            if c:
                upcoming_app.append(
                    [
                        app.pk,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.app_link,
                        app.status,
                        app.completed,
                        sta.first_name,
                    ]
                )

        completed_app = []  # approved manually inside
        # get all approved appointments
        for app in Appointment.objects.filter(staff=sta, completed=True).all():
            c = app.student
            if c:
                completed_app.append(
                    [sta.first_name, c.first_name, app.completed, app.pk]
                )

        messages.add_message(
            request,
            messages.INFO,
            "You have {0} pending appointments to approve.".format(
                pending_app_count),
        )

        return render(
            request,
            "appointments/staff/dashboard_sta.html",
            {
                "sta": sta,
                "pending_app": pending_app,
                "upcoming_app": upcoming_app,
                "app_completed": app_completed,
                "available_app": available_app,
                "completed_app": completed_app,
                "app_count": app_count,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# View all staff appointments
@login_required(login_url="login_sta.html")
def all_app_sta_view(request):
    if check_staff(request.user):
        # get information from database and render in html webpage
        sta = Staff.objects.get(staff_id=request.user.id)
        app_completed = (
            Appointment.objects.all().filter(staff=sta.id, completed=True).count()
        )
        available_app = (
            Appointment.objects.all().filter(staff=sta.id, status=False).count()
        )
        app_count = (
            models.Appointment.objects.all()
            .filter(
                staff=sta.id,
                status=True,
            )
            .count()
        )

        pending_app = []
        for app in Appointment.objects.filter(
            status=False, staff=sta.id, app_link__isnull=True, completed=False
        ).all():  # get unapproved appointments which have links not set and are not yet finished
            c = Student.objects.filter(id=app.student.id).first()
            if c:
                pending_app.append(
                    [
                        app.pk,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.status,
                        app.completed,
                    ]
                )

        upcoming_app = []
        for app in Appointment.objects.filter(
            status=False, staff=sta.id, app_link__isnull=True, completed=True
        ).all():  # get approved appointments which have links not set and are not yet finished
            c = Student.objects.filter(id=app.student.id).first()
            app.app_link = c.first_name
            if c:
                upcoming_app.append(
                    [
                        app.pk,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.app_link,
                        app.status,
                        app.completed,
                        sta.first_name,
                    ]
                )

        completed_app = []  # approved manually inside
        # get all approved appointments
        for app in Appointment.objects.filter(staff=sta.id, completed=True).all():
            c = app.student
            app.app_link = c.first_name
            if c:
                completed_app.append(
                    [
                        app.pk,
                        c.first_name,
                        c.last_name,
                        c.department,
                        app.app_date,
                        app.app_time,
                        app.description,
                        app.app_link,
                        app.status,
                        app.completed,
                        sta.first_name,
                    ]
                )

        return render(
            request,
            "appointments/staff/view_app_sta.html",
            {
                "sta": sta,
                "pending_app": pending_app,
                "upcoming_app": upcoming_app,
                "completed_app": completed_app,
                "app_completed": app_completed,
                "app_count": app_count,
                "available_app": available_app,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# Add appointment link action - can't seem to save link.... link = app_link?
@login_required(login_url="login_sta.html")
def add_link_sta_action(request, pk, link):
    if check_staff(request.user):
        # get information from database and render in html webpage
        appointment = Appointment.objects.get(id=pk)
        appointment.app_link = link
        appointment.save()
        return redirect(reverse("view_app_sta.html"))
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# View staff appointment's details, approve appointment or edit details - save & update doesn't work, complete works
@login_required(login_url="login_sta.html")
def app_details_sta_view(request, pk):
    if check_staff(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()

        app = Appointment.objects.filter(id=pk).first()  # get appointment
        sta = app.staff
        stu = app.student

        app.app_link = stu.first_name

        appointment_details = [
            sta.first_name,
            sta.last_name,
            sta.service_field,
            stu.first_name,
            stu.last_name,
            stu.department,
            stu.address,
            stu.postcode,
            stu.city,
            stu.country,
            app.app_date,
            app.app_time,
            app.app_link,
            app.description,
            app.status,
            app.completed,
            pk,
        ]  # render fields

        return render(
            request,
            "appointments/staff/view_app_details_sta.html",
            {
                "adm": adm,
                "sta": sta,
                "app": app,
                "stu": stu,
                "appointment_details": appointment_details,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_adm.html")


# Get an appointment
@login_required(login_url="login_sta.html")
def get_link_sta_action(request, pk):
    if check_staff(request.user):
        # get information from database
        appointment = Appointment.objects.get(id=pk)
        appointment.status = True  # approve appointment
        appointment.save()

        sta = appointment.staff
        esf = StaffServiceField.objects.filter(staff=sta).first()
        esf.app_total += 1  # add student to staff count
        esf.save()

        messages.add_message(request, messages.INFO, "Appointment approved!")
        return redirect(reverse("dashboard_sta.html"))
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# Complete an appointment - did I even use this?
@login_required(login_url="login_sta.html")
def complete_app_sta_action(request, pk):
    if check_staff(request.user):
        # get information from database and render in html webpage
        app = Appointment.objects.get(id=pk)
        app.completed = True
        app.save()

        messages.add_message(
            request, messages.INFO, "Appointment completed successfully!"
        )
        return redirect("view_app_sta.html")
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# View all approved appointments
@login_required(login_url="login_sta.html")
def approved_app_sta_view(request):
    if check_staff(request.user):
        sta = Staff.objects.get(staff_id=request.user.id)  # get staff

        incomplete_appointments = []
        for aca in ApprovedStudentAppointment.objects.filter(
            staff=sta
        ).all():  # get all student approved under this staff
            stu = aca.student
            if stu and not aca.completed_date:
                incomplete_appointments.append(
                    [
                        sta.first_name,
                        stu.first_name,
                        aca.approval_date,
                        aca.completed_date,
                        aca.pk,
                    ]
                )

        completed_appointments = []
        for aca in ApprovedStudentAppointment.objects.filter(
            staff=sta
        ).all():  # get all students approved under this staff
            stu = aca.student
            if stu and aca.completed_date:
                completed_appointments.append(
                    [
                        sta.first_name,
                        stu.first_name,
                        aca.approval_date,
                        aca.completed_date,
                        aca.pk,
                    ]
                )
        return render(
            request,
            "appointments/staff/view_approved_app_sta.html",
            {
                "incomplete_appointments": incomplete_appointments,
                "completed_appointments": completed_appointments,
            },
        )
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# View approved appointment's details
@login_required(login_url="login_sta.html")
def approved_app_details_sta_view(request, pk):
    if check_staff(request.user):
        # get information from database and render in html webpage
        aca = ApprovedStudentAppointment.objects.filter(id=pk).first()
        sta_d = Staff.objects.get(staff_id=request.user.id)
        sta_d = sta_d.service_field

        stu = aca.student
        sta = aca.staff
        approved_appointment_details = [
            aca.pk,
            sta.first_name,
            stu.first_name,
            aca.approval_date,
            aca.completed_date,
            aca.description,
        ]
        # med = Medicines.objects.all()
        return render(
            request,
            "appointments/staff/view_approved_app_details_sta.html",
            {
                "approved_appointment_details": approved_appointment_details,
                "sta_d": sta_d,
            },
        )
        # 'med': med})
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# staff feedback
@login_required(login_url="login_sta.html")
def feedback_sta_view(request):
    if check_staff(request.user):
        sta = Staff.objects.get(staff_id=request.user.id)
        feedback_form = forms.FeedbackForm()
        if request.method == "POST":
            feedback_form = forms.FeedbackForm(request.POST)
            if feedback_form.is_valid():  # if form is valid
                # get email from form
                email = feedback_form.cleaned_data["Email"]
                name = feedback_form.cleaned_data["Name"]  # get name from form
                subject = "You have a new Feedback from {}:<{}>".format(
                    name, feedback_form.cleaned_data["Email"]
                )  # get subject from form
                # get message from form
                message = feedback_form.cleaned_data["Message"]

                message = (
                    "Subject: {}\n"
                    "Date: {}\n"
                    "Message:\n\n {}".format(
                        dict(feedback_form.subject_choices).get(
                            feedback_form.cleaned_data["Subject"]
                        ),
                        datetime.datetime.now(),
                        feedback_form.cleaned_data["Message"],
                    )
                )

                try:
                    mail_admins(subject, message)
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Thank you for submitting your feedback.",
                    )

                    return redirect("feedback_sta.html")
                except:
                    feedback_form.add_error("Email", "Try again.")
                    return render(
                        request,
                        "appointments/staff/feedback_sta.html",
                        {"feedback_form": feedback_form},
                    )
        return render(
            request,
            "appointments/staff/feedback_sta.html",
            {"sta": sta, "feedback_form": feedback_form},
        )
    else:
        auth.logout(request)
        return redirect("login_sta.html")


# User check
def check_admin(user):  # check if user is admin
    return user.groups.filter(name="Admin").exists()


def check_student(user):  # check if user is student
    return user.groups.filter(name="Student").exists()


def check_staff(user):  # check if user is staff
    return user.groups.filter(name="Staff").exists()


# Appointment availability check
# check if staff is available in a given slot
def check_sta_availability(staff, dt, tm):
    tm = tm[:-3]  # separate AM/PM
    hr = tm[:-3]  # get hour reading
    mn = tm[-2:]  # get minute reading
    ftm = time(int(hr), int(mn), 0)  # create a time object
    app = Appointment.objects.all().filter(
        status=True, staff=staff, app_date=dt
    )  # get all appointments for a given sta and the given date

    # if time is not in between 9AM to 5PM, reject
    if ftm < time(9, 0, 0) or ftm > time(17, 0, 0):
        return False

    if (
        time(12, 0, 0) < ftm < time(13, 0, 0)
    ):  # if time is in between 12PM to 1PM, reject
        return False

    for a in app:
        if (
            ftm == a.app_time and dt == a.app_date
        ):  # if some other appointment has the same slot, reject
            return False

    return True


openai_api_key = "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"
openai.api_key = openai_api_key


def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="text-davinci-003",
        prompt=message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )

    print(response)
    answer = response[0].text.strip()


@login_required(login_url="chatbot-login")
def chatbot_view(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message,
                    response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'appointments/chat/chatbot.html', {'chats': chats})


def chatbot_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'appointments/chat/login.html', {'error_message': error_message})
    else:
        return render(request, 'appointments/chat/login.html')


def chatbot_logout(request):
    auth.logout(request)
    return redirect('login')
