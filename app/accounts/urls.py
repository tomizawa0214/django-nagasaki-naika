from django.urls import path

from app.accounts import views

urlpatterns = [
    # allauthのデフォルトと同じURL
    path("", views.LoginView.as_view(), name="account_login"),
    path("signup/", views.SignupView.as_view(), name="account_signup"),
    path("logout/", views.LogoutView.as_view(), name="account_logout"),
    # 独自URL
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/verify/", views.PasswordResetVerifyView.as_view(), name="password_reset_verify"),
    path(
        "password-reset/new-password/<uidb64>/<token>/",
        views.PasswordResetNewpasswordView.as_view(),
        name="password_reset_newpassword",
    ),
    path("password-reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("signup/confirm/", views.SignupConfirmView.as_view(), name="signup_confirm"),
    path("signup/verify/", views.SignupVerifyView.as_view(), name="signup_verify"),
    path("signup/done/<token>/", views.SignupDoneView.as_view(), name="signup_done"),
    path("mypage/password/", views.PasswordChangeView.as_view(), name="password_change"),
    path("mypage/password/done/", views.PasswordChangeDoneView.as_view(), name="password_change_done"),
]
