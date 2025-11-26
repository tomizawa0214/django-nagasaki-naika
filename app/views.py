from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import View

from app.seo_meta import *
from app.functions import *

from .forms import *


# =====================================================================================================
# 初期設定
# =====================================================================================================

# セッション管理
SESSION_KEY_APPOINTMENT = "appointment_data"

# =====================================================================================================
# マイページ
# =====================================================================================================
class MypageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # ログインユーザーを取得
        user_data = request.user

        # ログインユーザーの名前を取得
        user_name = user_data.name

        # テンプレートを描画
        return render(request, "mypage.html", {**meta_mypage, "user_name": user_name})


# =====================================================================================================
# 診察予約（初診 / 再診）
# =====================================================================================================
class AppointmentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # フォームを取得
        form = AppointmentVisitForm(request.POST or None)

        # テンプレートを描画
        return render(request, "appointment.html", {**meta_appointment, "form": form})

    def post(self, request, *args, **kwargs):

        # フォームを取得
        form = AppointmentVisitForm(request.POST or None)

        # バリデーションを実行
        if form.is_valid():

            # 初診or再診を取得
            visit = form.cleaned_data.get("visit")

            # 入力値を辞書に格納
            appointment_data = {
                "visit": visit
            }

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
        appointment_data = request.session.get(SESSION_KEY_APPOINTMENT)

        # セッションが無ければ入力画面へリダイレクト
        if not appointment_data:
            return redirect("appointment")

        # フォームを取得
        form = AppointmentQuestionnaireForm(request.POST or None)

        # テンプレートを描画
        return render(request, "appointment_questionnaire.html", {**meta_appointment_questionnaire, "form": form})

    def post(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = request.session.get(SESSION_KEY_APPOINTMENT)

        # セッションが無ければ入力画面へリダイレクト
        if not appointment_data:
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
        appointment_data = request.session.get(SESSION_KEY_APPOINTMENT)

        # セッションが無ければ入力画面へリダイレクト
        if not appointment_data:
            return redirect("appointment")

        # 初診 or 再診を取得
        visit = appointment_data.get("visit")

        # 初診の場合の戻るボタン
        if visit =="first":
            back_url = "appointment_questionnaire"

        # 再診の場合の戻るボタン
        if visit =="return":
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

        # フォームを取得
        form = AppointmentDatetimeForm(request.POST or None)

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
        appointment_data = request.session.get(SESSION_KEY_APPOINTMENT)

        # セッションが無ければ入力画面へリダイレクト
        if not appointment_data:
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
# プライバシーポリシー
# =====================================================================================================
class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})
