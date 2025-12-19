import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View

from .accounts.forms import *
from .forms import *
from .functions import *
from .seo_meta import *

# =====================================================================================================
# 初期設定
# =====================================================================================================

# ログ
logger = logging.getLogger(__name__)

# 登録ユーザーを取得
User = get_user_model()

# セッション管理
SESSION_KEY_APPOINTMENT = "session_appointment"
SESSION_KEY_APPOINTMENT_EDIT = "session_appointment_edit"
SESSION_KEY_CALENDAR_APPOINTMENT = "session_calendar_appointment"
SESSION_KEY_CALENDAR_APPOINTMENT_EDIT = "session_calendar_appointment_edit"
SESSION_KEY_QUESTIONNAIRE_EDIT = "session_questionnaire_edit"


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
            initial["visit"] = appointment_data.get("visit")

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

        # ボタンテキストを定義
        next_button_text = "次へ"

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key=SESSION_KEY_CALENDAR_APPOINTMENT)

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_str in settings.TIME_LIST:
                if day[time_str] != "closed":
                    value = f"{day['date_obj'].isoformat()}T{time_str}"
                    label = f"{day['date_obj']} {time_str}"
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
                "next_button_text": next_button_text,
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

        # ボタンテキストを定義
        next_button_text = "次へ"

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key=SESSION_KEY_CALENDAR_APPOINTMENT)

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_str in settings.TIME_LIST:
                if day[time_str] != "closed":
                    value = f"{day['date_obj'].isoformat()}T{time_str}"
                    label = f"{day['date_obj']} {time_str}"
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
                "next_button_text": next_button_text,
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
        dt = datetime.datetime.fromisoformat(appointment_data.get("appointment_dt"))
        date_obj = dt.date()
        time_str = dt.strftime("%H:%M")

        # 予約可否を判定
        status = status_check(
            date_obj=date_obj,
            time_str=time_str,
            closing_map=closing_map(),
            reservation_map=reservation_map(),
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

            # 問診票のバリデーション
            if visit == "first":

                # 問診票のフォームを取得
                q_form = AppointmentQuestionnaireForm(appointment_data)

                # バリデーションが失敗する場合は問診票ページへリダイレクト
                if not q_form.is_valid():
                    return redirect("appointment_questionnaire")

            # トランザクション内でまとめて処理
            with transaction.atomic():

                # 入力値を取得
                appointment_dt = timezone.make_aware(
                    datetime.datetime.fromisoformat(appointment_data.get("appointment_dt")),
                    timezone.get_current_timezone(),
                )
                user_family_name = form.cleaned_data.get("user_family_name")
                user_first_name = form.cleaned_data.get("user_first_name")
                email = form.cleaned_data.get("email")
                phone = form.cleaned_data.get("phone")
                birthdate = form.cleaned_data.get("birthdate")
                gender = form.cleaned_data.get("gender")
                card_number = form.cleaned_data.get("card_number") or None

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
                    symptom = q_form.cleaned_data.get("symptom")
                    symptom_other = q_form.cleaned_data.get("symptom_other") or None
                    symptom_start = datetime.date.fromisoformat(q_form.cleaned_data.get("symptom_start"))
                    medical_history = q_form.cleaned_data.get("medical_history")
                    has_medical_history = q_form.cleaned_data.get("has_medical_history") or None
                    under_treatment = q_form.cleaned_data.get("under_treatment")
                    has_under_treatment = q_form.cleaned_data.get("has_under_treatment") or None
                    current_medication = q_form.cleaned_data.get("current_medication")
                    has_current_medication = q_form.cleaned_data.get("has_current_medication") or None
                    smoking = q_form.cleaned_data.get("smoking")
                    has_smoking_per_day = q_form.cleaned_data.get("has_smoking_per_day") or None
                    has_smoking_years = q_form.cleaned_data.get("has_smoking_years") or None
                    has_quit_smoking_years = q_form.cleaned_data.get("has_quit_smoking_years") or None
                    has_until_smoking_years = q_form.cleaned_data.get("has_until_smoking_years") or None
                    alcohol = q_form.cleaned_data.get("alcohol")
                    alcohol_per_week = q_form.cleaned_data.get("alcohol_per_week") or None
                    alcohol_type = q_form.cleaned_data.get("alcohol_type") or None
                    alcohol_amount = q_form.cleaned_data.get("alcohol_amount") or None
                    allergy = q_form.cleaned_data.get("allergy")
                    has_allergy = q_form.cleaned_data.get("has_allergy") or None
                    pregnancy = q_form.cleaned_data.get("pregnancy")
                    especially = q_form.cleaned_data.get("especially") or None

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
                request.session.pop(SESSION_KEY_CALENDAR_APPOINTMENT, None)

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
# 予約の変更（予約確認）
# =====================================================================================================
class AppointmentDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # メタタグにURLを追加
        meta = {**meta_appointment_detail, "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/"}

        # ログインユーザーの当該予約データを取得
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

        # テンプレートを描画
        return render(
            request,
            "appointment_detail.html",
            {**meta, "appointment": appointment},
        )


# =====================================================================================================
# 予約の変更（日時変更）
# =====================================================================================================
class AppointmentDatetimeEditView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key=SESSION_KEY_CALENDAR_APPOINTMENT_EDIT)

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_str in settings.TIME_LIST:
                if day[time_str] != "closed":
                    value = f"{day['date_obj'].isoformat()}T{time_str}"
                    label = f"{day['date_obj']} {time_str}"
                    choices.append((value, label))

        # フォームを取得
        form = AppointmentDatetimeForm()

        # フォームの選択肢を定義
        form.fields["appointment_dt"].choices = choices

        # 戻るボタンのURLを定義
        back_url = "appointment_detail"

        # ボタンテキストを定義
        next_button_text = "日時を変更する"

        # メタタグにURLを追加
        meta = {
            **meta_appointment_datetime_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/datetime/edit/",
        }

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_datetime.html",
            {
                **meta,
                **calendar_data,
                "back_url": back_url,
                "next_button_text": next_button_text,
                "pk": pk,
                "form": form,
            },
        )

    def post(self, request, pk, *args, **kwargs):

        # カレンダーを取得
        calendar_data = build_calendar(request, session_key=SESSION_KEY_CALENDAR_APPOINTMENT_EDIT)

        # フォーム用の選択肢を格納
        choices = []
        for day in calendar_data["appointment_dt_list"]:
            for time_str in settings.TIME_LIST:
                if day[time_str] != "closed":
                    value = f"{day['date_obj'].isoformat()}T{time_str}"
                    label = f"{day['date_obj']} {time_str}"
                    choices.append((value, label))

        # フォームを取得
        form = AppointmentDatetimeForm(request.POST or None)

        # フォームの選択肢を定義
        form.fields["appointment_dt"].choices = choices

        # 戻るボタンのURLを定義
        back_url = "appointment_detail"

        # ボタンテキストを定義
        next_button_text = "日時を変更する"

        # メタタグにURLを追加
        meta = {
            **meta_appointment_datetime_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/datetime/edit",
        }

        # バリデーションを実行
        if form.is_valid():

            # 入力値を取得
            appointment_dt = timezone.make_aware(
                datetime.datetime.fromisoformat(form.cleaned_data.get("appointment_dt")),
                timezone.get_current_timezone(),
            )

            # トランザクション内でまとめて処理
            with transaction.atomic():

                # ログインユーザーの当該予約データを取得
                appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

                # 更新処理
                appointment.appointment_dt = appointment_dt
                appointment.save(update_fields=["appointment_dt", "updated_at"])

                # セッションを削除
                request.session.pop(SESSION_KEY_CALENDAR_APPOINTMENT_EDIT, None)

            # 完了ページへリダイレクト
            return redirect("appointment_edit_datetime_complete", pk=pk)

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_datetime.html",
            {
                **meta,
                **calendar_data,
                "back_url": back_url,
                "next_button_text": next_button_text,
                "pk": pk,
                "form": form,
            },
        )


# =====================================================================================================
# 予約の変更（完了）
# =====================================================================================================
class AppointmentDatetimeEditCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # メタタグにURLを追加
        meta = {
            **meta_appointment_datetime_edit_complete,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/datetime/edit/complete/",
        }

        # テンプレートを描画
        return render(request, "appointment_edit_datetime_complete.html", {**meta})


# =====================================================================================================
# 予約の変更（連絡先の変更）
# =====================================================================================================
class AppointmentContactEditView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # セッションを取得
        appointment_edit = session_check(request, session_key=SESSION_KEY_APPOINTMENT_EDIT)

        # ログインユーザーの当該予約データを取得
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

        # フォームの初期値を定義
        user = appointment.user
        initial = {
            "user_family_name": appointment.family_name or getattr(user, "family_name", None),
            "user_first_name": appointment.first_name or getattr(user, "first_name", None),
            "email": appointment.email or getattr(user, "email", None),
            "phone": appointment.phone or getattr(user, "phone", None),
            "birthdate": appointment.birthdate or getattr(user, "birthdate", None),
            "gender": appointment.gender or getattr(user, "gender", None),
            "card_number": appointment.card_number or getattr(user, "card_number", None),
            "privacy": True,
        }

        # セッションの選択を初期値に設定（戻る操作時に対応）
        if appointment_edit:
            initial = {
                "user_family_name": appointment_edit.get("user_family_name"),
                "user_first_name": appointment_edit.get("user_first_name"),
                "email": appointment_edit.get("email"),
                "phone": appointment_edit.get("phone"),
                "birthdate": appointment_edit.get("birthdate"),
                "gender": appointment_edit.get("gender"),
                "card_number": appointment_edit.get("card_number") or None,
                "privacy": True,
            }

        # フォームを取得
        form = AppointmentContactForm(initial=initial)

        # プライバシーポリシーは常に同意扱いでPOST送信
        form.fields["privacy"].widget = forms.HiddenInput()

        # メタタグにURLを追加
        meta = {
            **meta_appointment_contact_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/contact/edit/",
        }

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_contact.html",
            {
                **meta,
                "pk": pk,
                "form": form,
            },
        )

    def post(self, request, pk, *args, **kwargs):

        # フォームを取得
        form = AppointmentContactForm(request.POST or None)

        # メタタグにURLを追加
        meta = {
            **meta_appointment_contact_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/contact/edit/",
        }

        # バリデーションを実行
        if form.is_valid():

            # 現在日時を取得
            created_at = timezone.localtime(timezone.now())

            # 入力値を辞書に格納
            appointment_edit = {
                "user_family_name": form.cleaned_data.get("user_family_name"),
                "user_first_name": form.cleaned_data.get("user_first_name"),
                "email": form.cleaned_data.get("email"),
                "phone": form.cleaned_data.get("phone"),
                "birthdate": form.cleaned_data.get("birthdate").isoformat(),
                "gender": form.cleaned_data.get("gender"),
                "card_number": form.cleaned_data.get("card_number") or None,
                "privacy": form.cleaned_data.get("privacy"),
                "updated_at": created_at.isoformat(),
            }

            # セッションに保存
            request.session[SESSION_KEY_APPOINTMENT_EDIT] = appointment_edit

            # 確認ページへリダイレクト
            return redirect("appointment_edit_contact_confirm", pk=pk)

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_contact.html",
            {
                **meta,
                "pk": pk,
                "form": form,
            },
        )


# =====================================================================================================
# 予約の変更（変更確認）
# =====================================================================================================
class AppointmentContactEditConfirmView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # セッションを取得
        appointment_edit = session_check(request, session_key=SESSION_KEY_APPOINTMENT_EDIT)

        # セッション判定
        if appointment_edit is None:
            return redirect("appointment_detail", pk=pk)

        # メタタグにURLを追加
        meta = {
            **meta_appointment_contact_edit_confirm,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/contact/edit/confirm/",
        }

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_contact_confirm.html",
            {
                **meta,
                "pk": pk,
                **appointment_edit,
            },
        )

    def post(self, request, pk, *args, **kwargs):

        # セッションを取得
        appointment_edit = session_check(request, session_key=SESSION_KEY_APPOINTMENT_EDIT)

        # セッション判定
        if appointment_edit is None:
            return redirect("appointment_detail", pk=pk)

        # フォームを取得
        form = AppointmentContactForm(appointment_edit)

        # バリデーションを実行
        if form.is_valid():

            # 入力値を取得
            user_family_name = form.cleaned_data.get("user_family_name")
            user_first_name = form.cleaned_data.get("user_first_name")
            email = form.cleaned_data.get("email")
            phone = form.cleaned_data.get("phone")
            birthdate = form.cleaned_data.get("birthdate")
            gender = form.cleaned_data.get("gender")
            card_number = form.cleaned_data.get("card_number") or None

            # トランザクション内でまとめて処理
            with transaction.atomic():

                # ログインユーザーの当該予約データを取得
                appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

                # 変更情報をセット
                appointment.family_name = user_family_name
                appointment.first_name = user_first_name
                appointment.email = email
                appointment.phone = phone
                appointment.birthdate = birthdate
                appointment.gender = gender
                appointment.card_number = card_number

                # 更新処理
                appointment.save()

                # セッションを削除
                request.session.pop(SESSION_KEY_APPOINTMENT_EDIT, None)

            # 完了ページへリダイレクト
            return redirect("appointment_edit_contact_complete", pk=pk)

        # 仮にバリデーションが失敗する場合は予約確認ページへリダイレクト
        return redirect("appointment_detail", pk=pk)


# =====================================================================================================
# 予約の変更（完了）
# =====================================================================================================
class AppointmentContactEditCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # メタタグにURLを追加
        meta = {
            **meta_appointment_contact_edit_complete,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/contact/edit/complete/",
        }

        # テンプレートを描画
        return render(request, "appointment_edit_contact_complete.html", {**meta})


# =====================================================================================================
# 問診票を見る（予約確認）
# =====================================================================================================
class AppointmentQuestionnaireDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # メタタグにURLを追加
        meta = {
            **meta_appointment_questionnaire_detail,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/questionnaire/",
        }

        # ログインユーザーの当該予約データに紐づく問診票データを取得
        questionnaire = get_object_or_404(Questionnaire, appointment__pk=pk, appointment__user=request.user)

        # テンプレートを描画
        return render(
            request,
            "appointment_questionnaire_detail.html",
            {**meta, "pk": pk, "questionnaire": questionnaire},
        )


# =====================================================================================================
# 問診票の変更（変更）
# =====================================================================================================
class AppointmentQuestionnaireEditView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # セッションを取得
        questionnaire_edit = session_check(request, session_key=SESSION_KEY_QUESTIONNAIRE_EDIT)

        # ログインユーザーの当該予約データに紐づく問診票データを取得
        questionnaire = get_object_or_404(Questionnaire, appointment__pk=pk, appointment__user=request.user)

        # フォームの初期値を定義
        initial = {
            "symptom": questionnaire.symptom,
            "symptom_other": questionnaire.symptom_other,
            "symptom_start": questionnaire.symptom_start,
            "medical_history": questionnaire.medical_history,
            "has_medical_history": questionnaire.has_medical_history,
            "under_treatment": questionnaire.under_treatment,
            "has_under_treatment": questionnaire.has_under_treatment,
            "current_medication": questionnaire.current_medication,
            "has_current_medication": questionnaire.has_current_medication,
            "smoking": questionnaire.smoking,
            "has_smoking_per_day": questionnaire.has_smoking_per_day,
            "has_smoking_years": questionnaire.has_smoking_years,
            "has_quit_smoking_years": questionnaire.has_quit_smoking_years,
            "has_until_smoking_years": questionnaire.has_until_smoking_years,
            "alcohol": questionnaire.alcohol,
            "alcohol_per_week": questionnaire.alcohol_per_week,
            "alcohol_type": questionnaire.alcohol_type,
            "alcohol_amount": questionnaire.alcohol_amount,
            "allergy": questionnaire.allergy,
            "has_allergy": questionnaire.has_allergy,
            "pregnancy": questionnaire.pregnancy,
            "especially": questionnaire.especially,
        }

        # セッションの選択を初期値に設定（戻る操作時に対応）
        if questionnaire_edit:
            initial = {
                "symptom": questionnaire_edit.get("symptom"),
                "symptom_other": questionnaire_edit.get("symptom_other") or None,
                "symptom_start": questionnaire_edit.get("symptom_start"),
                "medical_history": questionnaire_edit.get("medical_history"),
                "has_medical_history": questionnaire_edit.get("has_medical_history") or None,
                "under_treatment": questionnaire_edit.get("under_treatment"),
                "has_under_treatment": questionnaire_edit.get("has_under_treatment") or None,
                "current_medication": questionnaire_edit.get("current_medication"),
                "has_current_medication": questionnaire_edit.get("has_current_medication") or None,
                "smoking": questionnaire_edit.get("smoking"),
                "has_smoking_per_day": questionnaire_edit.get("has_smoking_per_day") or None,
                "has_smoking_years": questionnaire_edit.get("has_smoking_years") or None,
                "has_quit_smoking_years": questionnaire_edit.get("has_quit_smoking_years") or None,
                "has_until_smoking_years": questionnaire_edit.get("has_until_smoking_years") or None,
                "alcohol": questionnaire_edit.get("alcohol"),
                "alcohol_per_week": questionnaire_edit.get("alcohol_per_week") or None,
                "alcohol_type": questionnaire_edit.get("alcohol_type") or None,
                "alcohol_amount": questionnaire_edit.get("alcohol_amount") or None,
                "allergy": questionnaire_edit.get("allergy"),
                "has_allergy": questionnaire_edit.get("has_allergy") or None,
                "pregnancy": questionnaire_edit.get("pregnancy"),
                "especially": questionnaire_edit.get("especially") or None,
            }

        # フォームを取得
        form = AppointmentQuestionnaireForm(initial=initial)

        # メタタグにURLを追加
        meta = {
            **meta_appointment_questionnaire_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/questionnaire/edit/",
        }

        # テンプレートを描画
        return render(request, "appointment_edit_questionnaire.html", {**meta, "pk": pk, "form": form})

    def post(self, request, pk, *args, **kwargs):

        # フォームを取得
        form = AppointmentQuestionnaireForm(request.POST or None)

        # メタタグにURLを追加
        meta = {
            **meta_appointment_questionnaire_edit,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/questionnaire/edit/",
        }

        # バリデーションを実行
        if form.is_valid():

            # 現在日時を取得
            created_at = timezone.localtime(timezone.now())

            # 入力値を辞書に格納
            questionnaire_edit = {
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
                "updated_at": created_at.isoformat(),
            }

            # セッションに保存
            request.session[SESSION_KEY_QUESTIONNAIRE_EDIT] = questionnaire_edit

            # 確認ページへリダイレクト
            return redirect("appointment_edit_questionnaire_confirm", pk=pk)

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_questionnaire.html",
            {
                **meta,
                "pk": pk,
                "form": form,
            },
        )


# =====================================================================================================
# 問診票の変更（変更確認）
# =====================================================================================================
class AppointmentQuestionnaireEditConfirmView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # セッションを取得
        questionnaire_edit = session_check(request, session_key=SESSION_KEY_QUESTIONNAIRE_EDIT)

        # セッション判定
        if questionnaire_edit is None:
            return redirect("appointment_questionnaire_detail", pk=pk)

        # メタタグにURLを追加
        meta = {
            **meta_appointment_questionnaire_edit_confirm,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/questionnaire/edit/confirm/",
        }

        # テンプレートを描画
        return render(
            request,
            "appointment_edit_questionnaire_confirm.html",
            {
                **meta,
                "pk": pk,
                **questionnaire_edit,
            },
        )

    def post(self, request, pk, *args, **kwargs):

        # セッションを取得
        questionnaire_edit = session_check(request, session_key=SESSION_KEY_QUESTIONNAIRE_EDIT)

        # セッション判定
        if questionnaire_edit is None:
            return redirect("appointment_questionnaire_detail", pk=pk)

        # フォームを取得
        form = AppointmentQuestionnaireForm(questionnaire_edit)

        # バリデーションを実行
        if form.is_valid():

            # トランザクション内でまとめて処理
            with transaction.atomic():

                # ログインユーザーの当該予約データに紐づく問診票データを取得
                questionnaire = get_object_or_404(Questionnaire, appointment__pk=pk, appointment__user=request.user)

                # 入力値を取得
                questionnaire.symptom = form.cleaned_data.get("symptom")
                questionnaire.symptom_other = form.cleaned_data.get("symptom_other") or None
                questionnaire.symptom_start = datetime.date.fromisoformat(form.cleaned_data.get("symptom_start"))
                questionnaire.medical_history = form.cleaned_data.get("medical_history")
                questionnaire.has_medical_history = form.cleaned_data.get("has_medical_history") or None
                questionnaire.under_treatment = form.cleaned_data.get("under_treatment")
                questionnaire.has_under_treatment = form.cleaned_data.get("has_under_treatment") or None
                questionnaire.current_medication = form.cleaned_data.get("current_medication")
                questionnaire.has_current_medication = form.cleaned_data.get("has_current_medication") or None
                questionnaire.smoking = form.cleaned_data.get("smoking")
                questionnaire.has_smoking_per_day = form.cleaned_data.get("has_smoking_per_day") or None
                questionnaire.has_smoking_years = form.cleaned_data.get("has_smoking_years") or None
                questionnaire.has_quit_smoking_years = form.cleaned_data.get("has_quit_smoking_years") or None
                questionnaire.has_until_smoking_years = form.cleaned_data.get("has_until_smoking_years") or None
                questionnaire.alcohol = form.cleaned_data.get("alcohol")
                questionnaire.alcohol_per_week = form.cleaned_data.get("alcohol_per_week") or None
                questionnaire.alcohol_type = form.cleaned_data.get("alcohol_type") or None
                questionnaire.alcohol_amount = form.cleaned_data.get("alcohol_amount") or None
                questionnaire.allergy = form.cleaned_data.get("allergy")
                questionnaire.has_allergy = form.cleaned_data.get("has_allergy") or None
                questionnaire.pregnancy = form.cleaned_data.get("pregnancy")
                questionnaire.especially = form.cleaned_data.get("especially") or None

                # 更新処理
                questionnaire.save()

                # セッションを削除
                request.session.pop(SESSION_KEY_QUESTIONNAIRE_EDIT, None)

            # 完了ページへリダイレクト
            return redirect("appointment_edit_questionnaire_complete", pk=pk)

        # 仮にバリデーションが失敗する場合は問診票の確認ページへリダイレクト
        return redirect("appointment_questionnaire_detail", pk=pk)


# =====================================================================================================
# 問診票の変更（完了）
# =====================================================================================================
class AppointmentQuestionnaireEditCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        # メタタグにURLを追加
        meta = {
            **meta_appointment_questionnaire_edit_complete,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/questionnaire/edit/complete/",
        }

        # テンプレートを描画
        return render(request, "appointment_edit_questionnaire_complete.html", {**meta})


# =====================================================================================================
# 予約の取消
# =====================================================================================================
class AppointmentDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # 直アクセスはマイページへリダイレクト
        return redirect("mypage")

    def post(self, request, pk, *args, **kwargs):

        # 予約データを取得
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

        # 予約データの来院日時を取得
        appointment_dt = timezone.localtime(appointment.appointment_dt)
        weekday = settings.WEEKDAYS[appointment_dt.weekday()]
        appointment_dt_str = f"{appointment_dt.strftime('%-m月%-d日')}({weekday}) {appointment_dt.strftime('%-H:%M')}〜"

        # 予約を削除
        appointment.delete()

        # メタタグにURLを追加
        meta = {
            **meta_appointment_delete,
            "url": f"{settings.BASE_URL}/mypage/appointment/{pk}/delete/",
        }

        # テンプレートを描画
        return render(
            request,
            "appointment_delete.html",
            {**meta, "appointment_dt_str": appointment_dt_str},
        )


# =====================================================================================================
# プライバシーポリシー
# =====================================================================================================
class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})


# =====================================================================================================
# 400 Bad Request: リクエスト自体が不正（形式ミスや不正な入力）で処理できない状態
# =====================================================================================================
def handler400_view(request, exception=None):

    # ログに記録
    logger.exception("status 400: %s", exception)

    # メタタグにURLを追加
    meta = {
        **meta_400,
        "url": request.build_absolute_uri(),
    }

    return render(request, "400.html", {**meta}, status=400)


# =====================================================================================================
# 403 Forbidden: 認証済みでも権限不足などでアクセスが許可されない状態
# =====================================================================================================
def handler403_view(request, exception=None):

    # ログに記録
    logger.exception("status 403: %s", exception)

    # メタタグにURLを追加
    meta = {
        **meta_403,
        "url": request.build_absolute_uri(),
    }

    return render(request, "403.html", {**meta}, status=403)


# =====================================================================================================
# 404 Not Found: 指定されたリソースやURLが存在しない状態
# =====================================================================================================
def handler404_view(request, exception=None):

    # ログに記録
    logger.warning("status 404: %s", exception)

    # メタタグにURLを追加
    meta = {
        **meta_404,
        "url": request.build_absolute_uri(),
    }

    return render(request, "404.html", {**meta}, status=404)


# =====================================================================================================
# 500 Internal Server Error: サーバー側で予期せぬエラーが起き、処理を完了できない状態
# =====================================================================================================
def handler500_view(request):

    # メタタグにURLを追加
    meta = {
        **meta_500,
        "url": request.build_absolute_uri(),
    }

    return render(request, "500.html", {**meta}, status=500)
