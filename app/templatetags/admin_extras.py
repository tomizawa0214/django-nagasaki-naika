from django import template

register = template.Library()


# =====================================================================================================
# 一覧画面: アプリケーションの順番指定
# =====================================================================================================
ORDER = [
    "accounts",
    "account",
    "app",
    "sites",
    "auth",
]
ORDER_MAP = {label: i for i, label in enumerate(ORDER)}


@register.filter
def sort_apps(app_list):
    return sorted(app_list, key=lambda a: ORDER_MAP.get(a["app_label"], len(ORDER_MAP)))


# =====================================================================================================
# 一覧画面: モデルの順番指定
# =====================================================================================================
MODEL_ORDER = [
    "Appointment",
    "Questionnaire",
    "RegularClosing",
    "SummerClosing",
    "NewYearClosing",
    "TempClosing",
]
MODEL_ORDER_MAP = {name: i for i, name in enumerate(MODEL_ORDER)}


@register.filter
def sort_models(models):
    return sorted(
        models,
        key=lambda m: MODEL_ORDER_MAP.get(m["object_name"], len(MODEL_ORDER_MAP)),
    )
