import datetime
from datetime import date

from django import template
from django.conf import settings

# =====================================================================================================
# 初期設定
# =====================================================================================================
register = template.Library()


# =====================================================================================================
# 性別
# =====================================================================================================
@register.filter
def gender_display(value):
    GENDER_MAP = dict(settings.GENDER_CHOICES)
    return GENDER_MAP.get(value)


# =====================================================================================================
# date型
# =====================================================================================================
@register.filter
def date_display(value):
    dt = date.fromisoformat(value)
    return dt


# =====================================================================================================
# 初診 または 再診
# =====================================================================================================
@register.filter
def visit_display(value):
    VISIT_MAP = dict(settings.VISIT_CHOICES)
    return VISIT_MAP.get(value)


# =====================================================================================================
# 本日はどうなさいましたか？
# =====================================================================================================
@register.filter
def symptom_display(values):
    SYMPTOM_MAP = dict(settings.SYMTOM_CHOICES)
    return [SYMPTOM_MAP.get(value, value) for value in values]


# =====================================================================================================
# 症状はいつ頃からありますか？
# =====================================================================================================
@register.filter
def symptom_start_display(value):
    dt = date.fromisoformat(value)
    today = datetime.date.today()
    diff = (today - dt).days
    if diff == 0:
        return "今日から"
    if diff == 1:
        return "昨日から"
    if 2 <= diff <= 3:
        return "2〜3日前から"
    if 4 <= diff <= 6:
        return "4〜6日前から"
    return "1週間以上前から"


# =====================================================================================================
# 過去に大きな病気で治療や手術を受けられたことはありますか？
# 現在、治療中の病気はありますか？
# 現在、飲んでいるお薬はありますか？
# お薬・食べ物のアレルギーはありますか？
# =====================================================================================================
@register.filter
def yes_or_no_display(value):
    YES_OR_NO_MAP = dict(settings.YES_OR_NO_CHOICES)
    return YES_OR_NO_MAP.get(value)


# =====================================================================================================
# 喫煙
# =====================================================================================================
@register.filter
def smoking_display(value):
    SMOKING_MAP = dict(settings.SMOKING_CHOICES)
    return SMOKING_MAP.get(value)


# =====================================================================================================
# 1日の喫煙本数
# =====================================================================================================
@register.filter
def smoking_per_day_display(value):
    if not value:
        return ""
    SMOKING_PER_DAY_MAP = dict(settings.SMOKING_PER_DAY_CHOICES)
    return SMOKING_PER_DAY_MAP.get(value)


# =====================================================================================================
# 喫煙の期間
# 禁煙するまでの喫煙期間
# =====================================================================================================
@register.filter
def years_display(value):
    if not value:
        return ""
    YEARS_MAP = dict(settings.YEARS_CHOICES)
    return YEARS_MAP.get(value)


# =====================================================================================================
# 禁煙の期間
# =====================================================================================================
@register.filter
def quit_smoking_years_display(value):
    if not value:
        return ""
    QUIT_SMOKING_YEARS_MAP = dict(settings.QUIT_SMOKING_YEARS_CHOICES)
    return QUIT_SMOKING_YEARS_MAP.get(value)


# =====================================================================================================
# 飲酒
# =====================================================================================================
@register.filter
def alcohol_display(value):
    ALCOHOL_MAP = dict(settings.ALCOHOL_CHOICES)
    return ALCOHOL_MAP.get(value)


# =====================================================================================================
# 飲酒の頻度
# =====================================================================================================
@register.filter
def alcohol_per_week_display(value):
    if not value:
        return ""
    ALCOHOL_PER_WEEK_MAP = dict(settings.ALCOHOL_PER_WEEK_CHOICES)
    return ALCOHOL_PER_WEEK_MAP.get(value)


# =====================================================================================================
# 現在、妊娠中あるいは妊娠の可能性、または授乳中ですか？
# =====================================================================================================
@register.filter
def pregnancy_display(value):
    PREGNANCY_MAP = dict(settings.PREGNANCY_CHOICES)
    return PREGNANCY_MAP.get(value)
