import datetime

from django.contrib import admin
from django.utils import timezone
from rangefilter.filters import DateRangeFilterBuilder

from .models import *


# =====================================================================================================
# フィルターのテキスト変更
# =====================================================================================================
class IsActiveFilter(admin.SimpleListFilter):
    title = "本登録ステータス"  # サイドバーに表示される見出し
    parameter_name = "is_active"  # URLクエリに使われるパラメータ名

    def lookups(self, request, model_admin):
        # 左側に表示する選択肢 (value, ラベル)
        return (
            ("1", "本登録済み"),
            ("0", "仮登録"),
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
class CustomUserAdmin(admin.ModelAdmin):

    # 一覧画面: 表示項目
    list_display = (
        "name",
        "email",
        "phone",
        "birthdate_with_age",
        "gender",
        "card_number",
        "formatted_created_at",
        "formatted_updated_at",
        "is_active",
    )

    # 一覧画面: 並び替え（登録日時の直近順）
    ordering = ("-created_at",)

    # 一覧画面: 検索ボックス
    search_fields = ("name", "email", "phone", "card_number")

    # 一覧画面: 絞り込み
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

    # 一覧画面: 日付ナビゲーション
    date_hierarchy = "created_at"

    # 一覧画面: 1ページあたりの表示件数
    list_per_page = 10000

    # 編集画面: 表示項目
    account = ("name", "email", "phone", "password", "birthdate", "gender", "card_number")
    auth = ("is_active", "is_staff")

    fieldsets = (
        ("登録情報", {"fields": account}),
        ("権限管理", {"fields": auth}),
    )

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
    def formatted_created_at(self, model):
        dt = timezone.localtime(model.created_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    formatted_created_at.short_description = "登録日時"

    # 更新日時の表示形式を変更
    def formatted_updated_at(self, model):
        dt = timezone.localtime(model.updated_at)
        return dt.strftime("%Y/%m/%d %H:%M")

    formatted_updated_at.short_description = "更新日時"


admin.site.register(CustomUser, CustomUserAdmin)
