import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from rangefilter.filters import DateRangeFilterBuilder

from .admin_forms import *
from .models import *


# =====================================================================================================
# フィルターのテキスト変更
# =====================================================================================================
class IsActiveFilter(admin.SimpleListFilter):
    title = "ログイン権限"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return (
            ("1", "利用可"),
            ("0", "利用不可"),
        )

    def queryset(self, request, queryset):
        # 選択肢が選ばれたときの絞り込み処理
        value = self.value()
        if value == "1":
            return queryset.filter(is_active=True)
        if value == "0":
            return queryset.filter(is_active=False)
        return queryset


# =====================================================================================================
# ユーザー情報
# =====================================================================================================
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreateForm

    # 一覧画面: 表示項目
    list_display = (
        "name_display",
        "email",
        "phone",
        "birthdate_with_age",
        "gender",
        "card_number",
        "created_at_display",
        "is_active",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 一覧画面: 検索項目
    search_fields = ("family_name", "first_name", "email", "phone", "card_number")

    # 一覧画面: 絞り込み項目
    list_filter = (
        (
            "created_at",
            DateRangeFilterBuilder(
                title="登録日",
                default_start=datetime.datetime.now(),
                default_end=datetime.datetime.now(),
            ),
        ),
        IsActiveFilter,
    )

    # 一覧画面: 日付階層ナビゲーション
    date_hierarchy = "created_at"

    # 一覧画面: 1ページあたりの表示件数
    list_per_page = 10000

    # 表示項目の定数
    account = ("family_name", "first_name", "email", "phone", "password", "birthdate", "gender", "card_number")
    auth = ("is_active",)
    access = ("last_login_display", "created_at_display", "updated_at_display")

    # 編集画面: 表示項目
    fieldsets = (
        ("登録情報", {"fields": account}),
        ("権限管理", {"fields": auth}),
        ("アクセス", {"fields": access}),
    )

    # 新規登録画面: 表示項目
    add_fieldsets = (
        ("登録情報", {"fields": account}),
        ("権限管理", {"fields": auth}),
        ("アクセス", {"fields": access}),
    )

    # 編集画面: 表示のみ（編集不可）
    readonly_fields = ("last_login_display", "created_at_display", "updated_at_display")

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
        return f"{model.birthdate.strftime('%Y年%-m月%-d日')}（{age}歳）"

    birthdate_with_age.short_description = "生年月日"

    # 登録日時の表示形式を変更
    def created_at_display(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    created_at_display.short_description = "登録日時"

    # 更新日時の表示形式を変更
    def updated_at_display(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    updated_at_display.short_description = "更新日時"

    # 最終ログイン日時の表示形式を変更
    def last_login_display(self, model):
        if not model.last_login:
            return "-"
        dt = timezone.localtime(model.last_login)
        return dt.strftime("%Y/%m/%d %H:%M")

    last_login_display.short_description = "最終ログイン"


admin.site.register(CustomUser, CustomUserAdmin)
