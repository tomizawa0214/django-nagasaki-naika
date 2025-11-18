from allauth.account import views
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import reverse_lazy

from .forms import *


# =====================================================================================================
# ログイン
# =====================================================================================================
class LoginView(views.LoginView):
    template_name = "account/login.html"
    form_class = CustomLoginForm
    extra_context = {
        "meta_robots": "index,follow",
        "meta_title": "長﨑医院ネット予約 | 群馬県前橋市",
        "meta_description": "群馬県前橋市住吉町にある長﨑医院のネット予約ページです。インターネットから24時間いつでも簡単に予約ができます。",
        "url": "https://yoyaku.nagasaki-naika.com",
    }


# =====================================================================================================
# パスワードリセット（メール入力）
# =====================================================================================================
class PasswordResetView(PasswordResetView):
    subject_template_name = "account/mail_template/password_reset_subject.txt"
    email_template_name = "account/mail_template/password_reset_message.txt"
    template_name = "account/password_reset.html"
    form_class = PasswordResetForm
    extra_context = {
        "meta_robots": "noindex,follow",
        "meta_title": "パスワードリセット | 長﨑医院ネット予約",
        "meta_description": "",
        "url": "https://yoyaku.nagasaki-naika.com/password-reset/",
    }
    extra_email_context = {
        "base_url": settings.BASE_URL,
    }
    success_url = reverse_lazy("password_reset_verify")


# =====================================================================================================
# パスワードリセット（メール認証）
# =====================================================================================================
class PasswordResetVerifyView(PasswordResetDoneView):
    template_name = "account/password_reset_verify.html"
    extra_context = {
        "meta_robots": "noindex,follow",
        "meta_title": "パスワードリセット（メール認証） | 長﨑医院ネット予約",
        "meta_description": "",
        "url": "https://yoyaku.nagasaki-naika.com/password-reset/verify/",
    }


# =====================================================================================================
# パスワードリセット（パスワード再設定）
# =====================================================================================================
class PasswordResetNewpasswordView(PasswordResetConfirmView):
    template_name = "account/password_reset_newpassword.html"
    form_class = SetPasswordForm
    extra_context = {
        "meta_robots": "noindex,follow",
        "meta_title": "パスワード再設定 | 長﨑医院ネット予約",
        "meta_description": "",
        "url": "https://yoyaku.nagasaki-naika.com/password-reset/new-password/",
    }
    success_url = reverse_lazy("password_reset_done")


# =====================================================================================================
# パスワードリセット（完了）
# =====================================================================================================
class PasswordResetDoneView(PasswordResetCompleteView):
    template_name = "account/password_reset_done.html"
    extra_context = {
        "meta_robots": "noindex,follow",
        "meta_title": "パスワードリセット完了 | 長﨑医院ネット予約",
        "meta_description": "",
        "url": "https://yoyaku.nagasaki-naika.com/password-reset/done/",
    }
