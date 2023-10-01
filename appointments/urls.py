from django.contrib.auth import views as auth_views
from django.urls import path

from appointments import views

urlpatterns = [
    # Account
    path("", views.login_view, name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="appointments/account/logout.html"),
        name="logout",
    ),
    path("blog/", views.blog_view, name="blog"),
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("chatbot-login/", views.chatbot_login, name="chatbot-login"),
    path("chatbot-logout/", views.chatbot_logout, name="chatbot-logout"),
    # path('wait-approval/', views.wait_approval_view, name='wait_approval.html'), # no need for this
    # Reset password
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="appointments/account/reset_password.html"
        ),
        name="reset_password.html",
    ),
    path(
        "reset_password_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="appointments/account/reset_password_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # Admin
    path(
        "register/admin/", views.register_adm_view, name="register_adm.html"
    ),  # Admin registration
    path("login/admin/", views.login_adm_view,
         name="login_adm.html"),  # Admin login
    path(
        "dashboard/admin/", views.dashboard_adm_view, name="dashboard_adm.html"
    ),  # Admin dashboard
    path(
        "profile/admin/", views.profile_adm_view, name="profile_adm.html"
    ),  # Admin profile
    # Admin - Appointments
    path(
        "view/appointments/", views.appointment_adm_view, name="appointment_adm.html"
    ),  # Admin profile
    path(
        "book-appointment-adm/", views.book_app_adm_view, name="book_app_adm.html"
    ),  # Book an appointment
    path(
        "approve-appointment/<int:pk>",
        views.approve_app_adm_action,
        name="approve_app_adm_action",
    ),  # Approve an appointment
    path(
        "appointment-admin/complete=<int:pk>",
        views.complete_app_adm_action,
        name="complete_app_adm_action",
    ),  # Complete appointment action
    path(
        "appointments/all/", views.all_app_adm_view, name="view_all_app_adm.html"
    ),  # View approved appointments
    path(
        "appointment/details/<int:pk>",
        views.app_details_adm_view,
        name="view_app_details_adm.html",
    ),  # View approved appointment's details
    # path('summary-report/', views.summary_report_adm_view, name="summary_report.html"),
    path("download-report/", views.dl_report_adm_action,
         name="dl_report_adm_action"),
    # Admin - Student
    path(
        "view/student/", views.student_adm_view, name="student_adm.html"
    ),  # Student section
    path(
        "approve/student/", views.approve_stu_adm_view, name="approve_stu.html"
    ),  # Approve student accounts
    path(
        "approve/student=<int:pk>",
        views.approve_stu_adm_action,
        name="approve_stu_action",
    ),  # Approve student action
    path(
        "view/all-students/", views.all_stu_adm_view, name="view_all_stu.html"
    ),  # View all student accounts
    # Admin - Staff
    path("view/staff/", views.staff_adm_view,
         name="staff_adm.html"),  # Staff section
    path(
        "approve/staff/", views.approve_sta_adm_view, name="approve_sta.html"
    ),  # Approve staff accounts
    path(
        "approve/staff=<int:pk>",
        views.approve_sta_adm_action,
        name="approve_sta_action",
    ),  # Approve staff action
    path(
        "view/all-staffs/", views.all_sta_adm_view, name="view_all_sta.html"
    ),  # View all staff accounts
    # Admin - Admin
    path("view/admins/", views.admin_adm_view,
         name="admin_adm.html"),  # Admins section
    path(
        "approve/admins/", views.approve_adm_adm_view, name="approve_adm.html"
    ),  # Approve staff accounts
    path(
        "approve/admin=<int:pk>",
        views.approve_adm_adm_action,
        name="approve_adm_action",
    ),  # Approve admin action
    path(
        "view/all-admins/", views.all_adm_adm_view, name="view_all_adm.html"
    ),  # View all staff accounts
    # Statistics
    path(
        "view/statistics/", views.statistics_adm_view, name="view_statistics_adm"
    ),  # View appointments statistics
    path("data", views.pivot_data, name="pivot_data"),
    # student
    path(
        "register/student/", views.register_stu_view, name="register_stu.html"
    ),  # student registration
    path(
        "login/student/", views.login_stu_view, name="login_stu.html"
    ),  # student login
    path(
        "profile/student/", views.profile_stu_view, name="profile_stu.html"
    ),  # student profile
    path(
        "book-appointment-stu/", views.book_app_stu_view, name="book_app_stu.html"
    ),  # Book an appointment
    path(
        "student/appointments", views.app_stu_view, name="view_app_stu.html"
    ),  # View pending appointments
    path(
        "student/appointments/all",
        views.all_app_stu_view,
        name="view_all_app_stu.html",
    ),  # View pending appointments
    path(
        "stu-appointment/details/<int:pk>",
        views.app_details_stu_view,
        name="view_app_details_stu.html",
    ),  # View appointment details
    path(
        "student/join-meeting/",
        views.join_meeting_stu_view,
        name="join_meeting_stu.html",
    ),  # Join meeting
    path(
        "appointment/report/<int:pk>",
        views.app_report_stu_view,
        name="app_report_stu.html",
    ),  # View appointment reports
    path("student/feedback/", views.feedback_stu_view, name="feedback_stu.html"),
    # Staff
    path(
        "register/staff/", views.register_sta_view, name="register_sta.html"
    ),  # Register staff
    path("login/staff/", views.login_sta_view,
         name="login_sta.html"),  # Login staff
    path(
        "profile/staff/", views.profile_sta_view, name="profile_sta.html"
    ),  # Staff profile
    path(
        "dashboard/staff/", views.dashboard_sta_view, name="dashboard_sta.html"
    ),  # Staff dashboard
    path(
        "staff/your-appointments/", views.all_app_sta_view, name="view_app_sta.html"
    ),  # View staff's appointments
    path(
        "staff/appointment-details/<int:pk>",
        views.app_details_sta_view,
        name="view_app_details_sta.html",
    ),  # Staff appointment's details
    path(
        "appointment/<int:pk>/<str:link>",
        views.add_link_sta_action,
        name="add_link_sta_action",
    ),  # Add link to appointment
    path(
        "staff/appointment/get=<int:pk>",
        views.get_link_sta_action,
        name="get_link_sta_action",
    ),  # Staff get appointment link action
    path(
        "staff/appointment/complete=<int:pk>",
        views.complete_app_sta_action,
        name="complete_app_sta_action",
    ),  # Complete appointment action
    path(
        "staff/approved-appointments/",
        views.approved_app_sta_view,
        name="view_approved_app_sta.html",
    ),
    path(
        "staff/approved-appointment-details/<int:pk>",
        views.approved_app_details_sta_view,
        name="view_approved_app_details_sta.html",
    ),
    path("staff/feedback/", views.feedback_sta_view, name="feedback_sta.html"),
    # Report (global)
    path(
        "download/report/id=<int:pk>",
        views.dl_app_report_action,
        name="dl_app_report_action",
    ),
    # Download report action
]
