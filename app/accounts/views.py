import email.utils
import logging
import unicodedata
from datetime import date

from allauth.account import views
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.views import View

from app.seo_meta import *

from .forms import *

# =====================================================================================================
# 初期設定
# =====================================================================================================

# 登録ユーザーを取得
User = get_user_model()

# セッション管理
SESSION_KEY_SIGNUP = "signup_data"

# ログ
logger = logging.getLogger(__name__)


# =====================================================================================================
# ログイン
# =====================================================================================================
class LoginView(views.LoginView):

    # テンプレートを指定
    template_name = "account/login.html"

    # フォームを指定
    form_class = CustomLoginForm

    # メタタグを定義
    extra_context = meta_login


# =====================================================================================================
# パスワードリセット（メール入力）
# =====================================================================================================
class PasswordResetView(PasswordResetView):

    # メールに使用する変数を定義
    extra_email_context = {
        "base_url": settings.BASE_URL,
    }

    # メール件名のテンプレートを指定
    subject_template_name = "account/mail_template/password_reset_subject.txt"

    # メール本文のテンプレートを指定
    email_template_name = "account/mail_template/password_reset_message.txt"

    # テンプレートを指定
    template_name = "account/password_reset.html"

    # フォームを指定
    form_class = CustomPasswordResetForm

    # メタタグを定義
    extra_context = meta_password_reset

    # 成功時のリダイレクト指定
    success_url = reverse_lazy("password_reset_verify")


# =====================================================================================================
# パスワードリセット（メール認証）
# =====================================================================================================
class PasswordResetVerifyView(PasswordResetDoneView):

    # テンプレートを指定
    template_name = "account/password_reset_verify.html"

    # メタタグを定義
    extra_context = meta_password_reset_verify


# =====================================================================================================
# パスワードリセット（パスワード再設定）
# =====================================================================================================
class PasswordResetNewpasswordView(PasswordResetConfirmView):

    # テンプレートを指定
    template_name = "account/password_reset_newpassword.html"

    # フォームを指定
    form_class = SetPasswordForm

    # メタタグを定義
    extra_context = meta_password_reset_newpassword

    # 成功時のリダイレクト指定
    success_url = reverse_lazy("password_reset_done")


# =====================================================================================================
# パスワードリセット（完了）
# =====================================================================================================
class PasswordResetDoneView(PasswordResetCompleteView):

    # テンプレートを指定
    template_name = "account/password_reset_done.html"

    # メタタグを定義
    extra_context = meta_password_reset_done


# =====================================================================================================
# ご利用登録（入力）
# =====================================================================================================
class SignupView(views.SignupView):

    # テンプレートを指定
    template_name = "account/signup.html"

    # フォームを指定
    form_class = CustomSignupForm

    # メタタグを定義
    extra_context = meta_signup

    # 戻る操作などでセッションが残っていればフォームの初期値に代入
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "GET":
            session_data = self.request.session.get(SESSION_KEY_SIGNUP)
            if session_data:
                initial = kwargs.get("initial", {}).copy()
                initial.update(session_data)
                kwargs["initial"] = initial
        return kwargs

    def post(self, request, *args, **kwargs):

        # フォームを取得
        form = CustomSignupForm(request.POST or None)

        # 同じメールアドレスかつ仮登録のアカウントは正規化のうえで削除（本登録忘れや入力間違いに対応）
        raw_email = form.data.get("email", "")
        normalized_email = unicodedata.normalize("NFKC", force_str(raw_email)).strip().lower()
        User.objects.filter(email=normalized_email, is_active=False).delete()

        # バリデーションを実行
        if form.is_valid():

            # 入力値を辞書に格納
            signup_data = {
                "user_family_name": form.cleaned_data["user_family_name"],
                "user_first_name": form.cleaned_data["user_first_name"],
                "email": form.cleaned_data["email"],
                "phone": form.cleaned_data["phone"],
                "password1": form.cleaned_data["password1"],
                "password2": form.cleaned_data["password1"],
                "birthdate": f"{form.cleaned_data['birthdate']}",
                "gender": form.cleaned_data["gender"],
                "card_number": form.cleaned_data["card_number"],
                "privacy": form.cleaned_data["privacy"],
            }

            # セッションに保存
            request.session[SESSION_KEY_SIGNUP] = signup_data

            # 確認画面へリダイレクト
            return redirect("signup_confirm")

        # バリデーション失敗の場合は入力画面にエラーを出力
        return render(
            request,
            "account/signup.html",
            {
                **meta_signup,
                "form": form,
            },
        )


# =====================================================================================================
# ご利用登録（確認）
# =====================================================================================================
class SignupConfirmView(View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        signup_data = request.session.get(SESSION_KEY_SIGNUP)

        # セッションが無ければ入力画面へリダイレクト
        if not signup_data:
            return redirect("signup")

        # 性別を出力用に変換
        gender_choices = dict(settings.GENDER_CHOICES)
        display_gender = gender_choices.get(signup_data.get("gender"))

        # 生年月日を出力用に変換
        birthdate_str = signup_data.get("birthdate")
        birthdate_dt = date.fromisoformat(birthdate_str)
        display_birthdate = f"{birthdate_dt.year}年{birthdate_dt.month}月{birthdate_dt.day}日"

        # テンプレートを描画
        return render(
            request,
            "account/signup_confirm.html",
            {
                **meta_signup_confirm,
                **signup_data,
                "display_gender": display_gender,
                "display_birthdate": display_birthdate,
            },
        )

    def post(self, request, *args, **kwargs):

        # 認証画面へリダイレクト
        return redirect("signup_verify")


# =====================================================================================================
# ご利用登録（メール認証）
# =====================================================================================================
class SignupVerifyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/signup_verify.html", {**meta_signup_verify})

    def post(self, request, *args, **kwargs):

        # セッションを取得
        signup_data = request.session.get(SESSION_KEY_SIGNUP)

        # セッションが無ければ入力画面へリダイレクト
        if not signup_data:
            return redirect("signup")

        # フォームを取得
        form = CustomSignupForm(signup_data)

        # バリデーションを実行
        if form.is_valid():

            # DB登録
            user_data = User()
            user_data.name = f"{signup_data['user_family_name']} {signup_data['user_first_name']}"
            user_data.email = signup_data["email"]
            user_data.phone = signup_data["phone"]
            user_data.set_password(signup_data["password1"])
            user_data.birthdate = signup_data["birthdate"]
            user_data.gender = signup_data["gender"]
            card_number = signup_data["card_number"]
            if card_number:
                user_data.card_number = card_number
            user_data.is_active = False
            user_data.save()

            # メールに使用する変数
            context = {
                "base_url": settings.BASE_URL,
                "token": dumps(user_data.pk),
                "user_data": user_data,
            }

            # メール設定
            subject = render_to_string("account/mail_template/signup_subject.txt", context)
            message = render_to_string("account/mail_template/signup_message.txt", context)
            from_email = email.utils.formataddr((settings.SITE_NAME, settings.EMAIL_HOST_USER))
            to_list = [user_data.email]

            # メール送信
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=to_list,
                )
            except Exception as exc:
                logger.exception("signup mail failed: %s", exc)
                return HttpResponse("メール送信に失敗しました")

            # セッションを削除
            del request.session[SESSION_KEY_SIGNUP]

            # テンプレートを描画
            return render(request, "account/signup_verify.html", {**meta_signup_verify})

        # 仮にバリデーションが失敗する場合は入力画面へリダイレクト
        return redirect("signup")


# =====================================================================================================
# ご利用登録（完了）
# =====================================================================================================
class SignupDoneView(View):
    def get(self, request, *args, **kwargs):

        # トークンの有効期限を24時間に定義
        timeout_seconds = getattr(settings, "ACTIVATION_TIMEOUT_SECONDS", 3600 * 24)

        # トークンを取得
        token = kwargs.get("token")

        # トークンのフラグ
        validlink = False

        # ユーザー本登録
        try:

            # ユーザーのidを取得
            user_data_pk = loads(token, max_age=timeout_seconds)

            # ユーザーを取得
            user_data = User.objects.filter(pk=user_data_pk).first()

            # ユーザー本登録
            if not user_data is None and not user_data.is_active:
                user_data.is_active = True
                user_data.save()

            # トークンのフラグ
            validlink = True

            # テンプレートを描画
            return render(request, "account/signup_done.html", {**meta_signup_done, "validlink": validlink})

        # トークンが期限切れの場合
        except SignatureExpired as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # トークンが間違っている場合
        except BadSignature as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # テンプレートを描画
        return render(request, "account/signup_done.html", {**meta_signup_failed, "validlink": validlink})
