from django.urls import path

from app.accounts import views

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/verify/", views.PasswordResetVerifyView.as_view(), name="password_reset_verify"),
    path("password-reset/new-password/<uidb64>/<token>/", views.PasswordResetNewpasswordView.as_view(), name="password_reset_newpassword"),
    path("password-reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
]
