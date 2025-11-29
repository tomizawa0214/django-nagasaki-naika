from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import View

from .accounts.forms import *
from .forms import *
from .functions import *
from .seo_meta import *

# =====================================================================================================
# 初期設定
# =====================================================================================================

# 登録ユーザーを取得
User = get_user_model()

# セッション管理
SESSION_KEY_APPOINTMENT = "appointment_data"
SESSION_KEY_APPOINTMENT_DT = "appointment_datetime"


# =====================================================================================================
# マイページ
# =====================================================================================================
class MypageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # ログインユーザーを取得
        user_data = request.user

        # ログインユーザーの名前を取得
        user_name = f"{user_data.family_name} {user_data.first_name}"

        # テンプレートを描画
        return render(request, "mypage.html", {**meta_mypage, "user_name": user_name})


# =====================================================================================================
# 診察予約（初診 / 再診）
# =====================================================================================================
class AppointmentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # 初期値を初期化（ラジオボタンの初期値設定がある場合）
        initial = {}

        # セッションの選択を初期値に設定（戻る操作時に対応）
        if "visit" in appointment_data:
            initial["visit"] = appointment_data["visit"]

        # フォームを取得
        form = AppointmentVisitForm(initial=initial)

        # テンプレートを描画
        return render(request, "appointment.html", {**meta_appointment, "form": form})

    def post(self, request, *args, **kwargs):

        # フォームを取得
        form = AppointmentVisitForm(request.POST or None)

        # バリデーションを実行
        if form.is_valid():

            # 初診or再診を取得
            visit = form.cleaned_data.get("visit")

            # 現在日時を取得
            created_at = timezone.localtime(timezone.now())

            # 入力値を辞書に格納
            appointment_data = {"visit": visit, "updated_at": created_at.isoformat()}

            # セッションに保存
            request.session[SESSION_KEY_APPOINTMENT] = appointment_data

            # 初診の場合
            if visit == "first":

                # 問診票ページへリダイレクト
                return redirect("appointment_questionnaire")

            # 再診の場合
            if visit == "return":

                # 日時選択ページへリダイレクト
                return redirect("appointment_datetime")

        # テンプレートを描画
        return render(request, "appointment.html", {**meta_appointment, "form": form})


# =====================================================================================================
# 診察予約（問診票）
# =====================================================================================================
class AppointmentQuestionnaireView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # 初期値を初期化（ラジオボタンの初期値設定がある場合）
        initial = {}

        # セッションの選択を初期値に設定（戻る操作時に対応）
        if "pregnancy" in appointment_data:
            initial = {
                "symptom": appointment_data.get("symptom"),
                "symptom_other": appointment_data.get("symptom_other") or None,
                "symptom_start": appointment_data.get("symptom_start"),
                "medical_history": appointment_data.get("medical_history"),
                "has_medical_history": appointment_data.get("has_medical_history") or None,
                "under_treatment": appointment_data.get("under_treatment"),
                "has_under_treatment": appointment_data.get("has_under_treatment") or None,
                "current_medication": appointment_data.get("current_medication"),
                "has_current_medication": appointment_data.get("has_current_medication") or None,
                "smoking": appointment_data.get("smoking"),
                "has_smoking_per_day": appointment_data.get("has_smoking_per_day") or None,
                "has_smoking_years": appointment_data.get("has_smoking_years") or None,
                "has_quit_smoking_years": appointment_data.get("has_quit_smoking_years") or None,
                "has_until_smoking_years": appointment_data.get("has_until_smoking_years") or None,
                "alcohol": appointment_data.get("alcohol"),
                "alcohol_per_week": appointment_data.get("alcohol_per_week") or None,
                "alcohol_type": appointment_data.get("alcohol_type") or None,
                "alcohol_amount": appointment_data.get("alcohol_amount") or None,
                "allergy": appointment_data.get("allergy"),
                "has_allergy": appointment_data.get("has_allergy") or None,
                "pregnancy": appointment_data.get("pregnancy"),
                "especially": appointment_data.get("especially") or None,
            }

        # フォームを取得
        form = AppointmentQuestionnaireForm(initial=initial)

        # テンプレートを描画
        return render(request, "appointment_questionnaire.html", {**meta_appointment_questionnaire, "form": form})

    def post(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # フォームを取得
        form = AppointmentQuestionnaireForm(request.POST or None)

        # バリデーションを実行
        if form.is_valid():

            # 入力値を辞書に格納
            appointment_data.update(
                {
                    "symptom": form.cleaned_data.get("symptom"),
                    "symptom_other": form.cleaned_data.get("symptom_other") or None,
                    "symptom_start": form.cleaned_data.get("symptom_start"),
                    "medical_history": form.cleaned_data.get("medical_history"),
                    "has_medical_history": form.cleaned_data.get("has_medical_history") or None,
                    "under_treatment": form.cleaned_data.get("under_treatment"),
                    "has_under_treatment": form.cleaned_data.get("has_under_treatment") or None,
                    "current_medication": form.cleaned_data.get("current_medication"),
                    "has_current_medication": form.cleaned_data.get("has_current_medication") or None,
                    "smoking": form.cleaned_data.get("smoking"),
                    "has_smoking_per_day": form.cleaned_data.get("has_smoking_per_day") or None,
                    "has_smoking_years": form.cleaned_data.get("has_smoking_years") or None,
                    "has_quit_smoking_years": form.cleaned_data.get("has_quit_smoking_years") or None,
                    "has_until_smoking_years": form.cleaned_data.get("has_until_smoking_years") or None,
                    "alcohol": form.cleaned_data.get("alcohol"),
                    "alcohol_per_week": form.cleaned_data.get("alcohol_per_week") or None,
                    "alcohol_type": form.cleaned_data.get("alcohol_type") or None,
                    "alcohol_amount": form.cleaned_data.get("alcohol_amount") or None,
                    "allergy": form.cleaned_data.get("allergy"),
                    "has_allergy": form.cleaned_data.get("has_allergy") or None,
                    "pregnancy": form.cleaned_data.get("pregnancy"),
                    "especially": form.cleaned_data.get("especially") or None,
                }
            )

            # セッションに保存
            request.session[SESSION_KEY_APPOINTMENT] = appointment_data

            # 日時選択ページへリダイレクト
            return redirect("appointment_datetime")

        # テンプレートを描画
        return render(request, "appointment_questionnaire.html", {**meta_appointment_questionnaire, "form": form})


# =====================================================================================================
# 診察予約（日時選択）
# =====================================================================================================
class AppointmentDatetimeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # 初診 or 再診を取得
        visit = appointment_data.get("visit")

        # 初診の場合の戻るボタン
        if visit == "first":
            back_url = "appointment_questionnaire"

        # 再診の場合の戻るボタン
        if visit == "return":
            back_url = "appointment"

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key="appointment_datetime")

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_data in settings.TIME_LIST:
                if day[time_data] != "closed":
                    value = f"{day['date_data'].isoformat()}T{time_data}"
                    label = f"{day['date_data']} {time_data}"
                    choices.append((value, label))

        # セッションの選択を初期値に設定（戻る操作時に対応）
        appointment_dt = appointment_data.get("appointment_dt")
        initial = {"appointment_dt": appointment_dt}

        # フォームを取得（戻る操作時はセッションの選択を初期値に設定）
        form = AppointmentDatetimeForm(initial=initial)

        # フォームの選択肢を定義
        form.fields["appointment_dt"].choices = choices

        # テンプレートを描画
        return render(
            request,
            "appointment_datetime.html",
            {
                **meta_appointment_datetime,
                **calendar_data,
                "back_url": back_url,
                "form": form,
            },
        )

    def post(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # 初診 or 再診を取得
        visit = appointment_data.get("visit")

        # 初診の場合の戻るボタン
        if visit == "first":
            back_url = "appointment_questionnaire"

        # 再診の場合の戻るボタン
        if visit == "return":
            back_url = "appointment"

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key=SESSION_KEY_APPOINTMENT_DT)

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_data in settings.TIME_LIST:
                if day[time_data] != "closed":
                    value = f"{day['date_data'].isoformat()}T{time_data}"
                    label = f"{day['date_data']} {time_data}"
                    choices.append((value, label))

        # フォームを取得
        form = AppointmentDatetimeForm(request.POST or None)

        # フォームの選択肢を定義
        form.fields["appointment_dt"].choices = choices

        # バリデーションを実行
        if form.is_valid():

            # 入力値を辞書に格納
            appointment_data.update(
                {
                    "appointment_dt": form.cleaned_data.get("appointment_dt"),
                }
            )

            # セッションに保存
            request.session[SESSION_KEY_APPOINTMENT] = appointment_data

            # 連絡先入力ページへリダイレクト
            return redirect("appointment_contact")

        # テンプレートを描画
        return render(
            request,
            "appointment_datetime.html",
            {
                **meta_appointment_datetime,
                **calendar_data,
                "back_url": back_url,
                "form": form,
            },
        )


# =====================================================================================================
# 診察予約（連絡先入力）
# =====================================================================================================
class AppointmentContactView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # ログインユーザーを取得
        user_data = request.user

        # フォームの初期値を定義
        initial = {
            "user_family_name": user_data.family_name,
            "user_first_name": user_data.first_name,
            "email": user_data.email,
            "phone": user_data.phone,
            "birthdate": user_data.birthdate,
            "gender": user_data.gender,
            "card_number": user_data.card_number,
        }

        # セッションの選択を初期値に設定（戻る操作時に対応）
        if "privacy" in appointment_data:
            initial = {
                "user_family_name": appointment_data.get("user_family_name"),
                "user_first_name": appointment_data.get("user_first_name"),
                "email": appointment_data.get("email"),
                "phone": appointment_data.get("phone"),
                "birthdate": appointment_data.get("birthdate"),
                "gender": appointment_data.get("gender"),
                "card_number": appointment_data.get("card_number") or None,
                "privacy": appointment_data.get("privacy"),
            }

        # フォームを取得
        form = AppointmentContactForm(initial=initial)

        # テンプレートを描画
        return render(
            request,
            "appointment_contact.html",
            {
                **meta_appointment_contact,
                "form": form,
            },
        )

    def post(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # フォームを取得
        form = AppointmentContactForm(request.POST or None)

        # バリデーションを実行
        if form.is_valid():

            # 入力値を辞書に格納
            appointment_data.update(
                {
                    "user_family_name": form.cleaned_data.get("user_family_name"),
                    "user_first_name": form.cleaned_data.get("user_first_name"),
                    "email": form.cleaned_data.get("email"),
                    "phone": form.cleaned_data.get("phone"),
                    "birthdate": f"{form.cleaned_data.get('birthdate')}",
                    "gender": form.cleaned_data.get("gender"),
                    "card_number": form.cleaned_data.get("card_number") or None,
                    "privacy": form.cleaned_data.get("privacy"),
                }
            )

            # セッションに保存
            request.session[SESSION_KEY_APPOINTMENT] = appointment_data

            # 確認ページへリダイレクト
            return redirect("appointment_confirm")

        # テンプレートを描画
        return render(
            request,
            "appointment_contact.html",
            {
                **meta_appointment_contact,
                "form": form,
            },
        )


# =====================================================================================================
# 診察予約（確認）
# =====================================================================================================
class AppointmentConfirmView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        print(appointment_data)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # テンプレートを描画
        return render(
            request,
            "appointment_confirm.html",
            {
                **meta_appointment_confirm,
                **appointment_data,
            },
        )

    def post(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT)

        # セッション判定
        if appointment_data is None:
            return redirect("appointment")

        # フォームを取得
        form = AppointmentContactForm(appointment_data)

        # 予約可否を判定


        # バリデーションを実行
        if form.is_valid():

            # DB登録
            # user_data = User()
            # user_data.family_name = signup_data.get("user_family_name")
            # user_data.first_name = signup_data.get("user_first_name")
            # user_data.email = user_email
            # user_data.phone = signup_data.get("phone")
            # user_data.set_password(signup_data.get("password1"))
            # user_data.birthdate = signup_data.get("birthdate")
            # user_data.gender = signup_data.get("gender")
            # user_data.card_number = signup_data.get("card_number")
            # user_data.is_active = False
            # user_data.save()

            # セッションを削除
            request.session.pop(SESSION_KEY_APPOINTMENT, None)

            # 完了ページへリダイレクト
            return redirect("appointment_complete")

        # 仮にバリデーションが失敗する場合は入力ページへリダイレクト
        return redirect("appointment")


# =====================================================================================================
# プライバシーポリシー
# =====================================================================================================
class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})
