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
    title = "ログイン権限"  # サイドバーに表示される見出し
    parameter_name = "is_active"  # URLクエリに使われるパラメータ名

    def lookups(self, request, model_admin):
        # 左側に表示する選択肢 (value, ラベル)
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
        "name",
        "email",
        "phone",
        "birthdate_with_age",
        "gender",
        "card_number",
        "display_created_at",
        "display_updated_at",
        "is_active",
    )

    # 一覧画面: 並び順
    ordering = ("-created_at",)

    # 一覧画面: 検索項目
    search_fields = ("name", "email", "phone", "card_number")

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
    account = ("name", "email", "phone", "password", "birthdate", "gender", "card_number")
    auth = ("is_active", "is_staff")
    access = ("display_last_login", "display_created_at", "display_updated_at")

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
    readonly_fields = ("display_last_login", "display_created_at", "display_updated_at")

    # 生年月日の表示形式を変更
    def birthdate_with_age(self, model):
        today = datetime.date.today()
        age = (
            today.year
            - model.birthdate.year
            - ((today.month, today.day) < (model.birthdate.month, model.birthdate.day))
        )
        return f"{model.birthdate:%Y年%m月%d日}（{age}歳）"

    birthdate_with_age.short_description = "生年月日"

    # 登録日時の表示形式を変更
    def display_created_at(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y年%m月%d日 %H:%M")

    display_created_at.short_description = "登録日時"

    # 更新日時の表示形式を変更
    def display_updated_at(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y年%m月%d日 %H:%M")

    display_updated_at.short_description = "更新日時"

    # 最終ログイン日時の表示形式を変更
    def display_last_login(self, model):
        if not model.last_login:
            return "-"
        dt = timezone.localtime(model.last_login)
        return dt.strftime("%Y年%m月%d日 %H:%M")

    display_last_login.short_description = "最終ログイン"


admin.site.register(CustomUser, CustomUserAdmin)
