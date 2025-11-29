from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
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

        # 現在時刻を取得
        dt_now = timezone.localtime(timezone.now())

        # ログインユーザーの予約情報を取得
        appointment_data = Appointment.objects.filter(user=user_data).order_by("-appointment_dt")

        # 来院予定の予約情報
        appointment_schedule = appointment_data.filter(appointment_dt__gte=dt_now)
        
        # 来院済みの予約情報
        appointment_done = appointment_data.filter(appointment_dt__lt=dt_now)

        # テンプレートを描画
        return render(
            request,
            "mypage.html",
            {
                **meta_mypage,
                "appointment_schedule": appointment_schedule,
                "appointment_done": appointment_done,
                "user_name": user_name,
            },
        )


# =====================================================================================================
# 診察予約（初診 / 再診）
# =====================================================================================================
class AppointmentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # セッションを取得
        appointment_data = session_check(request, session_key=SESSION_KEY_APPOINTMENT) or {}

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
                    "birthdate": form.cleaned_data.get("birthdate").isoformat(),
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

        # 予約可否の判定用
        dt = datetime.datetime.fromisoformat(appointment_data["appointment_dt"])
        date_data = dt.date()
        time_data = dt.strftime("%H:%M")
        tomorrow = datetime.date.today() + timedelta(days=1)
        weekday_index = date_data.weekday()
        regular_closing = list(RegularClosing.objects.values("weekday", "closed_hours"))
        summer_closing = list(SummerClosing.objects.values("start_date", "end_date"))
        new_year_closing = list(NewYearClosing.objects.values("start_date", "end_date"))
        temp_closing = list(TempClosing.objects.values("date", "closed_hours"))
        holiday_list = [
            date for date, _ in jpholiday.between(datetime.date.today(), datetime.date.today() + timedelta(days=60))
        ]

        # 来院日時のみをリストで取得
        reservation_appointment_dt = Appointment.objects.values_list("appointment_dt", flat=True)

        # 予約枠ごとの件数を格納する辞書を定義
        reservation_map = {}
        for appointment_dt in reservation_appointment_dt:

            # 現在のタイムゾーンに変換
            slot_dt = timezone.localtime(appointment_dt)

            # 30分単位に切り捨て
            slot_dt = slot_dt.replace(minute=(slot_dt.minute // 30) * 30, second=0, microsecond=0)

            # 枠を表すキーを作成
            key = (slot_dt.date(), slot_dt.time())

            # 同枠に対して件数を加算
            reservation_map[key] = reservation_map.get(key, 0) + 1

        # 予約可否を判定
        status = status_check(
            date_data=date_data,
            time_data=time_data,
            tomorrow=tomorrow,
            weekday_index=weekday_index,
            regular_closing=regular_closing,
            summer_closing=summer_closing,
            new_year_closing=new_year_closing,
            temp_closing=temp_closing,
            holiday_list=holiday_list,
            reservation_map=reservation_map,
        )

        # 予約不可の場合
        if status == "closed":

            # テンプレートを描画
            return render(
                request,
                "appointment_confirm.html",
                {
                    **meta_appointment_confirm,
                    **appointment_data,
                    "status": status,
                },
            )

        # バリデーションを実行
        if form.is_valid():

            # 入力値を取得
            visit = appointment_data.get("visit")
            appointment_dt = timezone.make_aware(
                datetime.datetime.fromisoformat(appointment_data["appointment_dt"]), timezone.get_current_timezone()
            )
            user_family_name = appointment_data.get("user_family_name")
            user_first_name = appointment_data.get("user_first_name")
            email = appointment_data.get("email")
            phone = appointment_data.get("phone")
            birthdate = datetime.date.fromisoformat(appointment_data["birthdate"])
            gender = appointment_data.get("gender")
            card_number = appointment_data.get("card_number") or None

            # トランザクション内でまとめて処理
            with transaction.atomic():

                # 予約情報をセット
                appointment_create = Appointment(
                    user=request.user,
                    visit=visit,
                    appointment_dt=appointment_dt,
                    family_name=user_family_name,
                    first_name=user_first_name,
                    email=email,
                    phone=phone,
                    birthdate=birthdate,
                    gender=gender,
                    card_number=card_number,
                )

                # 登録処理
                appointment_create.save()

                # 初診の場合
                if visit == "first":

                    # 入力値を取得
                    symptom = appointment_data.get("symptom")
                    symptom_other = appointment_data.get("symptom_other") or None
                    symptom_start = datetime.date.fromisoformat(appointment_data["symptom_start"])
                    medical_history = appointment_data.get("medical_history")
                    has_medical_history = appointment_data.get("has_medical_history") or None
                    under_treatment = appointment_data.get("under_treatment")
                    has_under_treatment = appointment_data.get("has_under_treatment") or None
                    current_medication = appointment_data.get("current_medication")
                    has_current_medication = appointment_data.get("has_current_medication") or None
                    smoking = appointment_data.get("smoking")
                    has_smoking_per_day = appointment_data.get("has_smoking_per_day") or None
                    has_smoking_years = appointment_data.get("has_smoking_years") or None
                    has_quit_smoking_years = appointment_data.get("has_quit_smoking_years") or None
                    has_until_smoking_years = appointment_data.get("has_until_smoking_years") or None
                    alcohol = appointment_data.get("alcohol")
                    alcohol_per_week = appointment_data.get("alcohol_per_week") or None
                    alcohol_type = appointment_data.get("alcohol_type") or None
                    alcohol_amount = appointment_data.get("alcohol_amount") or None
                    allergy = appointment_data.get("allergy")
                    has_allergy = appointment_data.get("has_allergy") or None
                    pregnancy = appointment_data.get("pregnancy")
                    especially = appointment_data.get("especially") or None

                    # 問診票をセット
                    questionnaire_create = Questionnaire(
                        appointment=appointment_create,
                        symptom=symptom,
                        symptom_other=symptom_other,
                        symptom_start=symptom_start,
                        medical_history=medical_history,
                        has_medical_history=has_medical_history,
                        under_treatment=under_treatment,
                        has_under_treatment=has_under_treatment,
                        current_medication=current_medication,
                        has_current_medication=has_current_medication,
                        smoking=smoking,
                        has_smoking_per_day=has_smoking_per_day,
                        has_smoking_years=has_smoking_years,
                        has_quit_smoking_years=has_quit_smoking_years,
                        has_until_smoking_years=has_until_smoking_years,
                        alcohol=alcohol,
                        alcohol_per_week=alcohol_per_week,
                        alcohol_type=alcohol_type,
                        alcohol_amount=alcohol_amount,
                        allergy=allergy,
                        has_allergy=has_allergy,
                        pregnancy=pregnancy,
                        especially=especially,
                    )

                    # 登録処理
                    questionnaire_create.save()

                # セッションを削除
                request.session.pop(SESSION_KEY_APPOINTMENT, None)

            # 完了ページへリダイレクト
            return redirect("appointment_complete")

        # 仮にバリデーションが失敗する場合は入力ページへリダイレクト
        return redirect("appointment")


# =====================================================================================================
# 診察予約（完了）
# =====================================================================================================
class AppointmentCompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(
            request,
            "appointment_complete.html",
            {
                **meta_appointment_complete,
            },
        )


# =====================================================================================================
# プライバシーポリシー
# =====================================================================================================
class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})
