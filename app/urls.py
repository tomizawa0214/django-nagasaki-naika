from django.urls import path

from app import views

urlpatterns = [
    path("mypage/", views.MypageView.as_view(), name="mypage"),
    path("mypage/appointment/", views.AppointmentView.as_view(), name="appointment"),
    path(
        "mypage/appointment/questionnaire/",
        views.AppointmentQuestionnaireView.as_view(),
        name="appointment_questionnaire",
    ),
    path("mypage/appointment/datetime/", views.AppointmentDatetimeView.as_view(), name="appointment_datetime"),
    path("mypage/appointment/contact/", views.AppointmentContactView.as_view(), name="appointment_contact"),
    path("mypage/appointment/confirm/", views.AppointmentConfirmView.as_view(), name="appointment_confirm"),
    path("mypage/appointment/complete/", views.AppointmentCompleteView.as_view(), name="appointment_complete"),
    path("mypage/appointment/<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment_detail"),
    path(
        "mypage/appointment/<int:pk>/datetime/edit/",
        views.AppointmentDatetimeEditView.as_view(),
        name="appointment_edit_datetime",
    ),
    path(
        "mypage/appointment/<int:pk>/datetime/edit/complete/",
        views.AppointmentDatetimeEditCompleteView.as_view(),
        name="appointment_edit_datetime_complete",
    ),
    path(
        "mypage/appointment/<int:pk>/contact/edit/",
        views.AppointmentContactEditView.as_view(),
        name="appointment_edit_contact",
    ),
    path(
        "mypage/appointment/<int:pk>/contact/edit/confirm/",
        views.AppointmentContactEditConfirmView.as_view(),
        name="appointment_edit_contact_confirm",
    ),
    path(
        "mypage/appointment/<int:pk>/contact/edit/complete/",
        views.AppointmentContactEditCompleteView.as_view(),
        name="appointment_edit_contact_complete",
    ),
    path(
        "mypage/appointment/<int:pk>/questionnaire/",
        views.AppointmentQuestionnaireDetailView.as_view(),
        name="appointment_questionnaire_detail",
    ),
    path(
        "mypage/appointment/<int:pk>/questionnaire/edit/",
        views.AppointmentQuestionnaireEditView.as_view(),
        name="appointment_edit_questionnaire",
    ),
    path(
        "mypage/appointment/<int:pk>/questionnaire/edit/confirm/",
        views.AppointmentQuestionnaireEditConfirmView.as_view(),
        name="appointment_edit_questionnaire_confirm",
    ),
    path(
        "mypage/appointment/<int:pk>/questionnaire/edit/complete/",
        views.AppointmentQuestionnaireEditCompleteView.as_view(),
        name="appointment_edit_questionnaire_complete",
    ),
    path(
        "mypage/appointment/<int:pk>/delete/",
        views.AppointmentDeleteView.as_view(),
        name="appointment_delete",
    ),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
]
