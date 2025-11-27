import email.utils
import logging
from datetime import date

from allauth.account import views
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
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
from django.utils import timezone
from django.views import View

from app.functions import *
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
    success_url = reverse_lazy("password_reset_complete")


# =====================================================================================================
# パスワードリセット（完了）
# =====================================================================================================
class PasswordResetCompleteView(PasswordResetCompleteView):

    # テンプレートを指定
    template_name = "account/password_reset_complete.html"

    # メタタグを定義
    extra_context = meta_password_reset_complete


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

        # バリデーションを実行
        if form.is_valid():

            # 現在日時を取得
            created_at = timezone.localtime(timezone.now())

            # 入力値を辞書に格納
            signup_data = {
                "user_family_name": form.cleaned_data.get("user_family_name"),
                "user_first_name": form.cleaned_data.get("user_first_name"),
                "email": form.cleaned_data.get("email"),
                "phone": form.cleaned_data.get("phone"),
                "password1": form.cleaned_data("password1"),
                "password2": form.cleaned_data("password1"),
                "birthdate": f"{form.cleaned_data.get('birthdate')}",
                "gender": form.cleaned_data.get("gender"),
                "card_number": form.cleaned_data.get("card_number"),
                "privacy": form.cleaned_data.get("privacy"),
                "updated_at": created_at.isoformat(),
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
        signup_data = session_check(request, session_key=SESSION_KEY_SIGNUP)

        # セッション判定
        if signup_data is None:
            return redirect("account_signup")

        # 性別を出力用に変換
        gender_choices = dict(settings.GENDER_CHOICES)
        gender_display = gender_choices.get(signup_data.get("gender"))

        # 生年月日を出力用に変換
        birthdate_str = signup_data.get("birthdate")
        birthdate_dt = date.fromisoformat(birthdate_str)
        birthdate_display = f"{birthdate_dt.year}年{birthdate_dt.month}月{birthdate_dt.day}日"

        # テンプレートを描画
        return render(
            request,
            "account/signup_confirm.html",
            {
                **meta_signup_confirm,
                **signup_data,
                "gender_display": gender_display,
                "birthdate_display": birthdate_display,
            },
        )

    def post(self, request, *args, **kwargs):

        # セッションを取得
        signup_data = session_check(request, session_key=SESSION_KEY_SIGNUP)

        # セッション判定
        if signup_data is None:
            return redirect("account_signup")

        # フォームを取得
        form = CustomSignupForm(signup_data)

        # バリデーションを実行
        if form.is_valid():

            # 同じメールアドレスかつ仮登録のアカウントを削除（本登録忘れや入力間違いに対応）
            user_email = signup_data["email"]
            User.objects.filter(email__iexact=user_email, is_active=False).delete()

            # DB登録
            user_data = User()
            user_data.name = f"{signup_data.get('user_family_name')} {signup_data.get('user_first_name')}"
            user_data.email = user_email
            user_data.phone = signup_data.get("phone")
            user_data.set_password(signup_data.get("password1"))
            user_data.birthdate = signup_data.get("birthdate")
            user_data.gender = signup_data.get("gender")
            user_data.card_number = signup_data.get("card_number")
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
            request.session.pop(SESSION_KEY_SIGNUP, None)

            # 認証画面へリダイレクト
            return redirect("signup_verify")

        # 仮にバリデーションが失敗する場合は入力画面へリダイレクト
        return redirect("account_signup")


# =====================================================================================================
# ご利用登録（メール認証）
# =====================================================================================================
class SignupVerifyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/signup_verify.html", {**meta_signup_verify})


# =====================================================================================================
# ご利用登録（完了）
# =====================================================================================================
class SignupCompleteView(View):
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
            return render(request, "account/signup_complete.html", {**meta_signup_complete, "validlink": validlink})

        # トークンが期限切れの場合
        except SignatureExpired as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # トークンが間違っている場合
        except BadSignature as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # テンプレートを描画
        return render(request, "account/signup_complete.html", {**meta_signup_failed, "validlink": validlink})


# =====================================================================================================
# パスワード変更（入力）
# =====================================================================================================
class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):

    # テンプレートを指定
    template_name = "account/password_change.html"

    # フォームを指定
    form_class = PasswordChangeForm

    # メタタグを定義
    extra_context = meta_password_change

    # 成功時のリダイレクト指定
    success_url = reverse_lazy("password_change_complete")


# =====================================================================================================
# パスワード変更（完了）
# =====================================================================================================
class PasswordChangeCompleteView(LoginRequiredMixin, PasswordChangeDoneView):

    # テンプレートを指定
    template_name = "account/password_change_complete.html"

    # メタタグを定義
    extra_context = meta_password_change_complete


# =====================================================================================================
# メールアドレス変更（入力）
# =====================================================================================================
class EmailChangeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # フォームを取得
        form = CustomEmailChangeForm(request.POST or None, current_email=request.user.email)

        # ログインユーザーを取得
        user_data = request.user

        # ログインユーザーのメールアドレスを取得
        user_email = user_data.email

        # テンプレートを描画
        return render(
            request,
            "account/email_change.html",
            {
                **meta_email_change,
                "form": form,
                "user_email": user_email,
            },
        )

    def post(self, request, *args, **kwargs):

        # ログインユーザーを取得
        user_data = request.user

        # フォームを取得
        form = CustomEmailChangeForm(request.POST or None, current_email=request.user.email)

        # バリデーションを実行
        if form.is_valid():

            # 新しいメールアドレスを取得
            user_new_email = form.cleaned_data.get("email")

            # メールに使用する変数
            context = {
                "base_url": settings.BASE_URL,
                "token": dumps(user_new_email),
                "user_data": user_data,
                "user_new_email": user_new_email,
            }

            # メール設定
            subject = render_to_string("account/mail_template/email_change_subject.txt", context)
            message = render_to_string("account/mail_template/email_change_message.txt", context)
            from_email = email.utils.formataddr((settings.SITE_NAME, settings.EMAIL_HOST_USER))
            to_list = [user_new_email]

            # メール送信
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=to_list,
                )
            except Exception as exc:
                logger.exception("email change mail failed: %s", exc)
                return HttpResponse("メール送信に失敗しました")

            # 確認画面へリダイレクト
            return redirect("email_change_verify")

        # ログインユーザーのメールアドレスを取得
        user_email = user_data.email

        # テンプレートを描画
        return render(
            request,
            "account/email_change.html",
            {
                **meta_email_change,
                "form": form,
                "user_email": user_email,
            },
        )


# =====================================================================================================
# メールアドレス変更（メール認証）
# =====================================================================================================
class EmailChangeVerifyView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/email_change_verify.html", {**meta_email_change_verify})


# =====================================================================================================
# メールアドレス変更（完了）
# =====================================================================================================
class EmailChangeCompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # トークンの有効期限を24時間に定義
        timeout_seconds = getattr(settings, "ACTIVATION_TIMEOUT_SECONDS", 3600 * 24)

        # トークンを取得
        token = kwargs.get("token")

        # トークンのフラグ
        validlink = False

        # メールアドレス登録
        try:

            # ユーザーの新しいメールアドレスを取得
            user_new_email = loads(token, max_age=timeout_seconds)

            # 新しいメールアドレスを登録
            request.user.email = user_new_email
            request.user.save()

            # トークンのフラグ
            validlink = True

            # テンプレートを描画
            return render(
                request, "account/email_change_complete.html", {**meta_email_change_complete, "validlink": validlink}
            )

        # トークンが期限切れの場合
        except SignatureExpired as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # トークンが間違っている場合
        except BadSignature as exc:
            logger.exception("signup register failed: %s", exc)
            pass

        # テンプレートを描画
        return render(
            request, "account/email_change_complete.html", {**meta_email_change_failed, "validlink": validlink}
        )


# =====================================================================================================
# 電話番号変更（入力）
# =====================================================================================================
class PhoneChangeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # フォームを取得
        form = PhoneChangeForm(request.POST or None, current_phone=request.user.phone)

        # ログインユーザーを取得
        user_data = request.user

        # ログインユーザーの電話番号を取得
        user_phone = user_data.phone

        # テンプレートを描画
        return render(
            request,
            "account/phone_change.html",
            {
                **meta_phone_change,
                "form": form,
                "user_phone": user_phone,
            },
        )

    def post(self, request, *args, **kwargs):

        # ログインユーザーを取得
        user_data = request.user

        # フォームを取得
        form = PhoneChangeForm(request.POST or None, current_phone=request.user.phone)

        # バリデーションを実行
        if form.is_valid():

            # ユーザーの新しい電話番号を取得
            user_new_phone = form.cleaned_data.get("phone")

            # 新しい電話番号を登録
            request.user.phone = user_new_phone
            request.user.save()

            # 確認画面へリダイレクト
            return redirect("phone_change_complete")

        # ログインユーザーの電話番号を取得
        user_phone = user_data.phone

        # テンプレートを描画
        return render(
            request,
            "account/phone_change.html",
            {
                **meta_phone_change,
                "form": form,
                "user_phone": user_phone,
            },
        )


# =====================================================================================================
# 電話番号変更（完了）
# =====================================================================================================
class PhoneChangeCompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/phone_change_complete.html", {**meta_phone_change_complete})


# =====================================================================================================
# 退会（確認）
# =====================================================================================================
class WithdrawView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/withdraw.html", {**meta_withdraw})

    def post(self, request, *args, **kwargs):

        # ログインユーザーのログイン権限を解除
        request.user.is_active = False
        request.user.save()

        # ログアウトを実行
        logout(request)

        # 退会完了ページへリダイレクト
        return redirect("withdraw_complete")


# =====================================================================================================
# 退会（完了）
# =====================================================================================================
class WithdrawCompleteView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "account/withdraw_complete.html", {**meta_withdraw_complete})


# =====================================================================================================
# ログアウト
# =====================================================================================================
class LogoutView(views.LogoutView):

    # テンプレートを指定
    template_name = "account/logout.html"

    # メタタグを定義
    extra_context = meta_logout

    def post(self, request, *args, **kwargs):

        # ログアウト処理
        if self.request.user.is_authenticated:
            self.logout()

        # テンプレートを描画
        return render(request, "account/logout.html", {**meta_logout})
