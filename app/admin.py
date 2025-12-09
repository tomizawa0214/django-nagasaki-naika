import datetime
import email.utils
import io
import logging
import zipfile
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder
from weasyprint import HTML

from .admin_forms import *
from .models import *

# =====================================================================================================
# 初期設定
# =====================================================================================================

# ログ
logger = logging.getLogger(__name__)


# =====================================================================================================
# 症状のフィルター
# =====================================================================================================
class SymptomFilter(admin.SimpleListFilter):
    title = "症状"
    parameter_name = "symptom"

    def lookups(self, request, model_admin):
        return settings.SYMTOM_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(symptom__icontains=f'"{value}"')
        return queryset


# =====================================================================================================
# 問診票の差し込み
# =====================================================================================================
class QuestionnaireInline(admin.StackedInline):
    model = Questionnaire
    form = QuestionnaireAdminForm
    can_delete = False
    extra = 0
    max_num = 1


# =====================================================================================================
# 診察予約
# =====================================================================================================
class AppointmentCustomAdmin(admin.ModelAdmin):

    inlines = (QuestionnaireInline,)

    # 一覧画面: 表示項目
    list_display = (
        "name_display",
        "appointment_dt_display",
        "visit",
        "email_display",
        "phone_display",
        "birthdate_with_age",
        "gender_display",
        "card_number_display",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-appointment_dt",)

    # 一覧画面: 検索項目
    search_fields = (
        "family_name",
        "first_name",
        "email",
        "phone",
        "card_number",
        "user__family_name",
        "user__first_name",
        "user__email",
        "user__phone",
        "user__card_number",
    )

    # 一覧画面: 絞り込み項目
    list_filter = (
        (
            "appointment_dt",
            DateRangeFilterBuilder(
                title="来院日",
                default_start=datetime.datetime.now(),
                default_end=datetime.datetime.now(),
            ),
        ),
    )

    # 一覧画面: 日付階層ナビゲーション
    date_hierarchy = "appointment_dt"

    # 一覧画面: 1ページあたりの表示件数
    list_per_page = 10000

    # 表示項目の定数
    appointment = ("appointment_dt", "visit")
    contact = ("user", "family_name", "first_name", "email", "phone", "birthdate", "gender", "card_number")
    access = ("created_at_display", "updated_at_display")

    # 編集画面: 表示項目
    fieldsets = (
        ("診察予約", {"fields": appointment}),
        ("連絡先", {"fields": contact}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("診察予約", {"fields": appointment}),
        ("連絡先", {"fields": contact}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display", "updated_at_display")

    # お名前の表示形式を変更
    def name_display(self, model):
        family_name = model.family_name or model.user.family_name
        first_name = model.first_name or model.user.first_name
        return f"{family_name} {first_name}"

    name_display.short_description = "お名前"

    # メールアドレスの表示形式を変更
    def email_display(self, model):
        return model.email or model.user.email

    email_display.short_description = "メールアドレス"

    # 電話番号の表示形式を変更
    def phone_display(self, model):
        return model.phone or model.user.phone

    phone_display.short_description = "電話番号"

    # 生年月日の表示形式を変更
    def birthdate_with_age(self, model):
        today = datetime.date.today()
        birthdate = model.birthdate or model.user.birthdate
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )
        return f"{birthdate.strftime('%Y年%-m月%-d日')}（{age}歳）"

    birthdate_with_age.short_description = "生年月日"

    # 性別の表示形式を変更
    def gender_display(self, model):
        return model.get_gender_display() or model.user.get_gender_display()

    gender_display.short_description = "性別"

    # 診察券番号の表示形式を変更
    def card_number_display(self, model):
        return model.card_number or model.user.card_number

    card_number_display.short_description = "診察券番号"

    # 来院日時の表示形式を変更
    def appointment_dt_display(self, model):
        dt = timezone.localtime(model.appointment_dt)
        weekday = settings.WEEKDAYS[dt.weekday()]
        return f"{dt.strftime('%Y年%-m月%-d日')}({weekday}) {dt.strftime('%H:%M')}"

    appointment_dt_display.short_description = "来院日時"

    # 受付日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "受付日時"

    # 更新日時の表示形式を変更
    def updated_at_display(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    updated_at_display.short_description = "更新日時"

    # 管理画面から手動で変更した場合はメールで通知
    def save_model(self, request, model, form, change):

        # 変更されていればTrue
        run = change and ("appointment_dt" in form.changed_data)

        # 変更前の値を取得
        if run and model.pk:
            before_appointment_dt = timezone.localtime(
                model.__class__.objects.only("appointment_dt").get(pk=model.pk).appointment_dt
            )

        # 変更を保存
        super().save_model(request, model, form, change)

        # 変更の場合に実行
        if run:

            # 変更後の値を取得
            after_appointment_dt = timezone.localtime(model.appointment_dt)
            user_family_name = model.family_name or model.user.family_name
            user_first_name = model.first_name or model.user.first_name
            user_email = model.email or model.user.email
            user_phone = model.phone or model.user.phone
            birthdate = model.birthdate or model.user.birthdate
            gender = model.get_gender_display() or model.user.get_gender_display()
            card_number = model.card_number or model.user.card_number
            created_at = timezone.localtime(model.created_at)

            # メールに使用する変数
            context = {
                "before_appointment_dt": before_appointment_dt,
                "after_appointment_dt": after_appointment_dt,
                "user_name": f"{user_family_name} {user_first_name}",
                "user_email": user_email,
                "user_phone": user_phone,
                "birthdate": birthdate,
                "gender": gender,
                "card_number": card_number,
                "created_at": created_at,
            }

            # メール設定
            subject = render_to_string("mail_template/subject/admin_appointment_dt_change.txt", context)
            message = render_to_string("mail_template/message/admin_appointment_dt_change.txt", context)
            from_email = email.utils.formataddr((settings.SITE_NAME, settings.EMAIL_HOST_USER))
            to_list = [user_email]

            # トランザクション処理のため関数化
            def safe_send_mail():
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=to_list,
                    )
                except Exception as exc:
                    logger.exception("admin appointment_dt change mail failed: %s", exc)

            # DB更新が確定した後にメール送信
            transaction.on_commit(lambda: safe_send_mail())

    # 管理画面から手動で削除の場合はメールで通知
    def send_delete_mail(self, snapshot):

        # 該当の予約データを取得
        appointment_dt = timezone.localtime(snapshot.appointment_dt)
        user_family_name = snapshot.family_name or snapshot.user.family_name
        user_first_name = snapshot.first_name or snapshot.user.first_name
        user_email = snapshot.email or snapshot.user.email
        user_phone = snapshot.phone or snapshot.user.phone
        birthdate = snapshot.birthdate or snapshot.user.birthdate
        gender = snapshot.get_gender_display() or snapshot.user.get_gender_display()
        card_number = snapshot.card_number or snapshot.user.card_number
        created_at = timezone.localtime(snapshot.created_at)

        # メールに使用する変数
        context = {
            "appointment_dt": appointment_dt,
            "user_name": f"{user_family_name} {user_first_name}",
            "user_email": user_email,
            "user_phone": user_phone,
            "birthdate": birthdate,
            "gender": gender,
            "card_number": card_number,
            "created_at": created_at,
        }

        # メール設定
        subject = render_to_string("mail_template/subject/admin_appointment_delete.txt", context)
        message = render_to_string("mail_template/message/admin_appointment_delete.txt", context)
        from_email = email.utils.formataddr((settings.SITE_NAME, settings.EMAIL_HOST_USER))
        to_list = [user_email]

        # トランザクション処理のため関数化
        def safe_send_mail():
            try:
                send_mail(subject=subject, message=message, from_email=from_email, recipient_list=to_list)
            except Exception as exc:
                logger.exception("admin appointment delete mail failed: %s", exc)

        # DB更新が確定した後にメール送信
        transaction.on_commit(lambda: safe_send_mail())

    # 管理画面から手動で削除の場合はメールで通知
    def delete_model(self, request, obj):
        snapshot = Appointment.objects.get(pk=obj.pk)
        super().delete_model(request, obj)
        self.send_delete_mail(snapshot)

    # 管理画面から手動で削除の場合はメールで通知（複数件削除に対応）
    def delete_queryset(self, request, queryset):
        snapshots = list(queryset)
        super().delete_queryset(request, queryset)
        for snapshot in snapshots:
            self.send_delete_mail(snapshot)


admin.site.register(Appointment, AppointmentCustomAdmin)


# =====================================================================================================
# 問診票
# =====================================================================================================
class QuestionnaireCustomAdmin(admin.ModelAdmin):
    form = QuestionnaireAdminForm
    action_form = QuestionnaireActionForm

    # 一覧画面: 表示項目
    list_display = (
        "appointment",
        "symptom_display",
        "especially_display",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-appointment__appointment_dt",)

    # 一覧画面: 絞り込み項目
    list_filter = (
        (
            "appointment__appointment_dt",
            DateRangeFilterBuilder(
                title="来院日",
                default_start=datetime.datetime.now(),
                default_end=datetime.datetime.now(),
            ),
        ),
        SymptomFilter,
    )

    # 一覧画面: 日付階層ナビゲーション
    date_hierarchy = "appointment__appointment_dt"

    # 一覧画面: 1ページあたりの表示件数
    list_per_page = 10000

    # 表示項目の定数
    appointment = ("appointment",)
    symptom = ("symptom", "symptom_other")
    symptom_start = ("symptom_start",)
    medical_history = ("medical_history", "has_medical_history")
    under_treatment = ("under_treatment", "has_under_treatment")
    current_medication = ("current_medication", "has_current_medication")
    smoking = (
        "smoking",
        "has_smoking_per_day",
        "has_smoking_years",
        "has_quit_smoking_years",
        "has_until_smoking_years",
    )
    alcohol = ("alcohol", "alcohol_per_week", "alcohol_type", "alcohol_amount")
    allergy = ("allergy", "has_allergy")
    pregnancy = ("pregnancy",)
    especially = ("especially",)
    access = ("created_at_display", "updated_at_display")

    # 編集画面: 表示項目
    fieldsets = (
        ("診察予約", {"fields": appointment}),
        ("本日はどうなさいましたか？", {"fields": symptom}),
        ("症状はいつ頃からありますか？", {"fields": symptom_start}),
        ("過去に大きな病気で治療や手術を受けられたことはありますか？", {"fields": medical_history}),
        ("現在、治療中の病気はありますか？", {"fields": under_treatment}),
        ("現在、飲んでいるお薬はありますか？", {"fields": current_medication}),
        ("喫煙について", {"fields": smoking}),
        ("飲酒について", {"fields": alcohol}),
        ("お薬・食べ物のアレルギーはありますか？", {"fields": allergy}),
        ("現在、妊娠中あるいは妊娠の可能性、または授乳中ですか？", {"fields": pregnancy}),
        ("特に調べてほしいこと、検査、治療がありましたらご記入ください", {"fields": especially}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("予約情報", {"fields": appointment}),
        ("本日はどうなさいましたか？", {"fields": symptom}),
        ("症状はいつ頃からありますか？", {"fields": symptom_start}),
        ("過去に大きな病気で治療や手術を受けられたことはありますか？", {"fields": medical_history}),
        ("現在、治療中の病気はありますか？", {"fields": under_treatment}),
        ("現在、飲んでいるお薬はありますか？", {"fields": current_medication}),
        ("喫煙について", {"fields": smoking}),
        ("飲酒について", {"fields": alcohol}),
        ("お薬・食べ物のアレルギーはありますか？", {"fields": allergy}),
        ("現在、妊娠中あるいは妊娠の可能性、または授乳中ですか？", {"fields": pregnancy}),
        ("特に調べてほしいこと、検査、治療がありましたらご記入ください", {"fields": especially}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display", "updated_at_display")

    # PDFダウンロードボタンの設置
    actions = ["download_pdf"]

    # 症状の表示を変更
    def symptom_display(self, model):
        label_map = dict(settings.SYMTOM_CHOICES)
        return "、 ".join(label_map.get(value, value) for value in model.symptom)

    symptom_display.short_description = "症状"

    # 特に調べてほしいことの表示を改行ありに変更
    def especially_display(self, model):
        if model.especially:
            return format_html(model.especially.replace("\n", "<br>"))
        return ""

    especially_display.short_description = "特に調べてほしいこと等"

    # 受付日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "受付日時"

    # 更新日時の表示形式を変更
    def updated_at_display(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    updated_at_display.short_description = "更新日時"

    # PDFダウンロード
    def download_pdf(self, request, queryset):
        if not queryset.exists():
            return

        # 現在日時を取得
        dt_now = timezone.localtime(timezone.now())

        # static ファイルのURLを取得
        static_root = Path(settings.STATIC_ROOT)

        # 本番環境 or 検品環境の場合
        if static_root.exists():
            static_base = static_root.as_uri().rstrip("/")

        # 開発環境の場合
        else:
            static_base = request.build_absolute_uri(static("")).rstrip("/")

        # 1件ならそのまま返す
        if queryset.count() == 1:
            q = queryset.first()
            context = {
                "pk": q.appointment_id,
                "questionnaire": q,
                "dt_now": dt_now,
            }
            html_str = render_to_string("questionnaire_write.html", context, request=request)
            html_str = (
                html_str.replace('href="/static/', f'href="{static_base}/')
                .replace("href='/static/", f"href='{static_base}/")
                .replace('src="/static/', f'src="{static_base}/')
                .replace("src='/static/", f"src='{static_base}/")
            )
            pdf = HTML(string=html_str, base_url=static_base).write_pdf()

            filename_utf8 = f"問診票_{dt_now.strftime("%Y%m%d%H%M")}.pdf"
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = (
                'attachment; filename="questionnaire.pdf"; ' f"filename*=UTF-8''{quote(filename_utf8)}"
            )
            return resp

        # 複数件ならZipにまとめる
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, q in enumerate(queryset, start=1):
                context = {
                    "pk": q.appointment_id,
                    "questionnaire": q,
                    "dt_now": dt_now,
                }
                html_str = render_to_string("questionnaire_write.html", context, request=request)
                html_str = (
                    html_str.replace('href="/static/', f'href="{static_base}/')
                    .replace("href='/static/", f"href='{static_base}/")
                    .replace('src="/static/', f'src="{static_base}/')
                    .replace("src='/static/", f"src='{static_base}/")
                )
                pdf_bytes = HTML(string=html_str, base_url=static_base).write_pdf()
                filename = f"問診票_{i}.pdf"
                zf.writestr(filename, pdf_bytes)

        buffer.seek(0)
        zip_name = f"問診票_{dt_now.strftime("%Y%m%d%H%M")}.zip"
        resp = HttpResponse(buffer.getvalue(), content_type="application/zip")
        resp["Content-Disposition"] = (
            'attachment; filename="questionnaires.zip"; ' f"filename*=UTF-8''{quote(zip_name)}"
        )
        return resp

    download_pdf.short_description = "PDFをダウンロード"


admin.site.register(Questionnaire, QuestionnaireCustomAdmin)


# =====================================================================================================
# 休診日
# =====================================================================================================
class RegularClosingCustomAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "weekday",
        "closed_hours",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 表示項目の定数
    setting = ("weekday", "closed_hours")
    access = ("created_at_display",)

    # 編集画面: 表示項目
    fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display",)

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(RegularClosing, RegularClosingCustomAdmin)


# =====================================================================================================
# 夏季休診
# =====================================================================================================
class SummerClosingCustomAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "summer_closing_display",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 表示項目の定数
    setting = ("start_date", "end_date")
    access = ("created_at_display",)

    # 編集画面: 表示項目
    fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display",)

    # 開始日と終了日の表示形式を変更
    def summer_closing_display(self, model):
        return f"{model.start_date.strftime("%Y年%-m月%-d日")}～{model.end_date.strftime("%-m月%-d日")}"

    summer_closing_display.short_description = "夏季休診期間"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(SummerClosing, SummerClosingCustomAdmin)


# =====================================================================================================
# 年末年始休診
# =====================================================================================================
class NewYearClosingCustomAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "new_year_closing_display",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 表示項目の定数
    setting = ("start_date", "end_date")
    access = ("created_at_display",)

    # 編集画面: 表示項目
    fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display",)

    # 開始日と終了日の表示形式を変更
    def new_year_closing_display(self, model):
        return f"{model.start_date.strftime("%Y年%-m月%-d日")}～{model.end_date.strftime("%-m月%-d日")}"

    new_year_closing_display.short_description = "年末年始の休診期間"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(NewYearClosing, NewYearClosingCustomAdmin)


# =====================================================================================================
# 臨時休診日
# =====================================================================================================
class TempClosingCustomAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "date_display",
        "closed_hours",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 表示項目の定数
    setting = ("date", "closed_hours")
    access = ("created_at_display",)

    # 編集画面: 表示項目
    fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("設定項目", {"fields": setting}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("created_at_display",)

    # 臨時休診日の表示形式を変更
    def date_display(self, model):
        return model.date.strftime("%Y年%-m月%-d日")

    date_display.short_description = "臨時休診日"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(TempClosing, TempClosingCustomAdmin)
