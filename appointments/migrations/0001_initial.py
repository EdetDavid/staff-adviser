# Generated by Django 4.2.5 on 2023-10-01 07:56

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("username", models.CharField(max_length=200, null=True, unique=True)),
                ("email", models.EmailField(max_length=254, null=True, unique=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="AppointmentRating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(5),
                            django.core.validators.MinValueValidator(0),
                        ],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Staff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        default="default.png", upload_to="profile_pictures"
                    ),
                ),
                ("first_name", models.CharField(default="first_name", max_length=100)),
                ("last_name", models.CharField(default="last_name", max_length=100)),
                ("dob", models.DateField(default=datetime.date.today)),
                ("address", models.CharField(default="address", max_length=300)),
                ("city", models.CharField(default="city", max_length=100)),
                ("country", models.CharField(default="country", max_length=100)),
                ("postcode", models.IntegerField(default=0)),
                (
                    "service_field",
                    models.CharField(
                        choices=[
                            ("Academics", "Academics"),
                            ("Career", "Career"),
                            (
                                "Technology and Digital Literacy",
                                "Technology and Digital Literacy",
                            ),
                            (
                                "Mental Health and Wellness",
                                "Mental Health and Wellness",
                            ),
                        ],
                        default="Service and Repair",
                        max_length=50,
                    ),
                ),
                ("status", models.BooleanField(default=False)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Staff",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        default="default.png",
                        null=True,
                        upload_to="profile_pictures",
                    ),
                ),
                ("first_name", models.CharField(default="first_name", max_length=100)),
                ("last_name", models.CharField(default="last_name", max_length=100)),
                ("dob", models.DateField(default=datetime.date.today)),
                ("department", models.CharField(default="department", max_length=300)),
                ("address", models.CharField(default="address", max_length=300)),
                ("city", models.CharField(default="city", max_length=100)),
                ("country", models.CharField(default="country", max_length=100)),
                ("postcode", models.IntegerField(default=0)),
                ("status", models.BooleanField(default=False)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Student",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StaffServiceField",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("app_total", models.IntegerField(default=0)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="StaffServiceField",
                        to="appointments.staff",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("response", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApprovedStudentAppointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("approval_date", models.DateField()),
                ("description", models.TextField()),
                ("completed_date", models.DateField(blank=True, null=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="StaffApprovedApp",
                        to="appointments.staff",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="StudentApprovedApp",
                        to="appointments.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField(max_length=500)),
                ("app_link", models.TextField(blank=True, null=True)),
                ("app_date", models.DateField(blank=True, null=True)),
                ("app_time", models.TextField(blank=True, null=True)),
                ("status", models.BooleanField(default=False)),
                ("completed", models.BooleanField(default=False)),
                ("rating", models.IntegerField(default=0)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="StaffApp",
                        to="appointments.staff",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="StudentApp",
                        to="appointments.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Admin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        default="default.png", upload_to="profile_pictures"
                    ),
                ),
                ("first_name", models.CharField(default="first_name", max_length=100)),
                ("last_name", models.CharField(default="last_name", max_length=100)),
                ("dob", models.DateField(default=datetime.date.today)),
                ("address", models.CharField(default="address", max_length=300)),
                ("city", models.CharField(default="city", max_length=100)),
                ("country", models.CharField(default="country", max_length=100)),
                ("postcode", models.IntegerField(default=0)),
                ("status", models.BooleanField(default=False)),
                (
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Admin",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]