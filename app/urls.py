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
    # path("mypage/appointment/complete/", views.AppointmentCompleteView.as_view(), name="appointment_complete"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
]
