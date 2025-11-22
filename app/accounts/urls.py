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
    path("password-reset/complete/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("signup/confirm/", views.SignupConfirmView.as_view(), name="signup_confirm"),
    path("signup/verify/", views.SignupVerifyView.as_view(), name="signup_verify"),
    path("signup/complete/<token>/", views.SignupCompleteView.as_view(), name="signup_complete"),
    path("mypage/password/", views.PasswordChangeView.as_view(), name="password_change"),
    path("mypage/password/complete/", views.PasswordChangeCompleteView.as_view(), name="password_change_complete"),
    path("mypage/email/", views.EmailChangeView.as_view(), name="email_change"),
    path("mypage/email/verify/", views.EmailChangeVerifyView.as_view(), name="email_change_verify"),
    path("mypage/email/complete/<token>/", views.EmailChangeCompleteView.as_view(), name="email_change_complete"),
    path("mypage/phone/", views.PhoneChangeView.as_view(), name="phone_change"),
    path("mypage/phone/complete/", views.PhoneChangeCompleteView.as_view(), name="phone_change_complete"),
    path("mypage/withdraw/", views.WithdrawView.as_view(), name="withdraw"),
    path("mypage/withdraw/complete/", views.WithdrawCompleteView.as_view(), name="withdraw_complete"),
]
