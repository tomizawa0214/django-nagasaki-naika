import datetime

from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder

from .admin_forms import *
from .models import *


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
        "user",
        "appointment_dt_display",
        "visit",
        "name_display",
        "email",
        "phone",
        "birthdate_with_age",
        "gender",
        "card_number",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-appointment_dt",)

    # 一覧画面: 検索項目
    search_fields = ("family_name", "first_name", "email", "phone", "card_number")

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
        return f"{model.family_name} {model.first_name}"

    name_display.short_description = "お名前"

    # 生年月日の表示形式を変更
    def birthdate_with_age(self, model):
        today = datetime.date.today()
        age = (
            today.year
            - model.birthdate.year
            - ((today.month, today.day) < (model.birthdate.month, model.birthdate.day))
        )
        return f"{model.birthdate:%Y年%-m月%-d日}（{age}歳）"

    birthdate_with_age.short_description = "生年月日"

    # 来院日時の表示形式を変更
    def appointment_dt_display(self, model):
        dt = timezone.localtime(model.appointment_dt)
        weekday = settings.WEEKDAYS[dt.weekday()]
        return f"{dt.strftime('%Y年%-m月%-d日')}({weekday}) {dt.strftime('%H:%M')}"

    appointment_dt_display.short_description = "来院日時"

    # 受付日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    created_at_display.short_description = "受付日時"

    # 更新日時の表示形式を変更
    def updated_at_display(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    updated_at_display.short_description = "更新日時"


admin.site.register(Appointment, AppointmentCustomAdmin)


# =====================================================================================================
# 問診票
# =====================================================================================================
class QuestionnaireCustomAdmin(admin.ModelAdmin):
    form = QuestionnaireAdminForm

    # 一覧画面: 表示項目
    list_display = (
        "appointment",
        "symptom_display",
        "especially_display",
        "created_at_display",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 一覧画面: 絞り込み項目
    list_filter = (SymptomFilter,)

    # 一覧画面: 日付階層ナビゲーション
    date_hierarchy = "created_at"

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
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    created_at_display.short_description = "受付日時"

    # 更新日時の表示形式を変更
    def updated_at_display(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    updated_at_display.short_description = "更新日時"


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
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

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
        return f"{model.start_date.strftime("%Y年%-m月%-d日")}～{model.end_date.strftime("%Y年%-m月%-d日")}"

    summer_closing_display.short_description = "夏季休診期間"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

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
        return f"{model.start_date.strftime("%Y年%-m月%-d日")}～{model.end_date.strftime("%Y年%-m月%-d日")}"

    new_year_closing_display.short_description = "年末年始の休診期間"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

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
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(TempClosing, TempClosingCustomAdmin)
