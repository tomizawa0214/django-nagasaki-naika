from django.contrib import admin
from django.utils import timezone

from .models import *


# =====================================================================================================
# 休診日
# =====================================================================================================
class RegularClosingCustomAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "weekday_display",
        "closed_hours_display",
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

    # 休診の曜日の表示形式を変更
    def weekday_display(self, model):
        return model.get_weekday_display()

    weekday_display.short_description = "休診の曜日"

    # 休診の時間帯の表示形式を変更
    def closed_hours_display(self, obj):
        return obj.get_closed_hours_display()

    closed_hours_display.short_description = "休診の時間帯"

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
        "closed_hours_display",
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

    # 休診の時間帯の表示形式を変更
    def closed_hours_display(self, obj):
        return obj.get_closed_hours_display()

    closed_hours_display.short_description = "休診の時間帯"

    # 更新日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y年%-m月%-d日 %H:%M")

    created_at_display.short_description = "更新日時"


admin.site.register(TempClosing, TempClosingCustomAdmin)
