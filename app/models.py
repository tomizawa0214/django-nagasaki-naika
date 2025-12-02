from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# =====================================================================================================
# 診察予約
# =====================================================================================================
class Appointment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="登録ユーザー"
    )
    visit = models.CharField("初診 または 再診", max_length=100, choices=settings.VISIT_CHOICES)
    appointment_dt = models.DateTimeField("来院日時")
    family_name = models.CharField("お名前 （姓）", max_length=100, blank=True, null=True)
    first_name = models.CharField("お名前 （名）", max_length=100, blank=True, null=True)
    email = models.EmailField("メールアドレス", max_length=256, blank=True, null=True)
    phone = models.CharField("電話番号", max_length=13, blank=True, null=True)
    birthdate = models.DateField("生年月日", blank=True, null=True)
    gender = models.CharField("性別", max_length=10, choices=settings.GENDER_CHOICES, blank=True, null=True)
    card_number = models.CharField("診察券番号", max_length=10, blank=True, null=True)
    created_at = models.DateTimeField("受付日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        family_name = self.user.family_name
        first_name = self.user.first_name
        dt = timezone.localtime(self.appointment_dt)
        weekday = settings.WEEKDAYS[dt.weekday()]
        return f"{family_name} {first_name} 【{dt.strftime('%Y年%-m月%-d日')}({weekday}) {dt.strftime('%H:%M')}】"

    class Meta:
        verbose_name = "診察予約"
        verbose_name_plural = "診察予約"


# =====================================================================================================
# 問診票
# =====================================================================================================
class Questionnaire(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, verbose_name="予約情報")
    symptom = models.JSONField("症状", default=list)
    symptom_other = models.CharField("その他の症状", blank=True, null=True)
    symptom_start = models.DateField("はじまりの時期")
    medical_history = models.CharField("ある / ない", max_length=100, choices=settings.YES_OR_NO_CHOICES)
    has_medical_history = models.CharField("過去の治療や手術", blank=True, null=True)
    under_treatment = models.CharField("ある / ない", max_length=100, choices=settings.YES_OR_NO_CHOICES)
    has_under_treatment = models.CharField("ある / ない", blank=True, null=True)
    current_medication = models.CharField("飲んでいるお薬", max_length=100, choices=settings.YES_OR_NO_CHOICES)
    has_current_medication = models.CharField("飲んでいるお薬", blank=True, null=True)
    smoking = models.CharField("煙草", max_length=100, choices=settings.SMOKING_CHOICES)
    has_smoking_per_day = models.CharField(
        "1日の喫煙本数", max_length=100, choices=settings.SMOKING_PER_DAY_CHOICES, blank=True, null=True
    )
    has_smoking_years = models.CharField(
        "喫煙の期間", max_length=100, choices=settings.YEARS_CHOICES, blank=True, null=True
    )
    has_quit_smoking_years = models.CharField(
        "禁煙の期間", max_length=100, choices=settings.QUIT_SMOKING_YEARS_CHOICES, blank=True, null=True
    )
    has_until_smoking_years = models.CharField(
        "禁煙するまでの喫煙期間", max_length=100, choices=settings.YEARS_CHOICES, blank=True, null=True
    )
    alcohol = models.CharField("飲酒", max_length=100, choices=settings.ALCOHOL_CHOICES)
    alcohol_per_week = models.CharField(
        "1週間の飲酒の頻度", max_length=100, choices=settings.ALCOHOL_PER_WEEK_CHOICES, blank=True, null=True
    )
    alcohol_type = models.CharField("飲酒の種類", blank=True, null=True)
    alcohol_amount = models.CharField("飲酒の量", blank=True, null=True)
    allergy = models.CharField("ある / ない", max_length=100, choices=settings.YES_OR_NO_CHOICES)
    has_allergy = models.CharField("お薬・食べ物のアレルギー", blank=True, null=True)
    pregnancy = models.CharField("妊娠について", max_length=100, choices=settings.PREGNANCY_CHOICES)
    especially = models.TextField("特記事項", blank=True, null=True)
    created_at = models.DateTimeField("受付日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        family_name = self.appointment.user.family_name
        first_name = self.appointment.user.first_name
        dt = timezone.localtime(self.appointment.appointment_dt)
        weekday = settings.WEEKDAYS[dt.weekday()]
        return f"{family_name} {first_name} 【{dt.strftime('%Y年%-m月%-d日')}({weekday}) {dt.strftime('%H:%M')}】"

    class Meta:
        verbose_name = "問診票"
        verbose_name_plural = "問診票"


# =====================================================================================================
# 休診日
# =====================================================================================================
class RegularClosing(models.Model):
    weekday = models.CharField("休診の曜日", choices=settings.CLOSED_WEEKDAY_CHOICES, max_length=10, unique=True)
    closed_hours = models.CharField(
        "休診の時間帯",
        max_length=10,
        choices=settings.CLOSED_TIME_CHOICES,
        default="all_day",
    )
    created_at = models.DateTimeField("変更日時", auto_now=True)

    def __str__(self):
        return f"{self.get_weekday_display()} ({self.get_closed_hours_display()})"

    class Meta:
        verbose_name = "休診日"
        verbose_name_plural = "休診日"


# =====================================================================================================
# 夏季休診
# =====================================================================================================
class SummerClosing(models.Model):
    start_date = models.DateField("開始日")
    end_date = models.DateField("終了日")
    created_at = models.DateTimeField("変更日時", auto_now=True)

    def __str__(self):
        return f"{self.start_date.strftime("%Y年%-m月%-d日")}～{self.end_date.strftime("%Y年%-m月%-d日")}"

    # バリデーション
    def clean(self):
        super().clean()
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "終了日は開始日より後の日付にしてください。"})

    class Meta:
        verbose_name = "夏季休診"
        verbose_name_plural = "夏季休診"


# =====================================================================================================
# 年末年始休診
# =====================================================================================================
class NewYearClosing(models.Model):
    start_date = models.DateField("開始日")
    end_date = models.DateField("終了日")
    created_at = models.DateTimeField("変更日時", auto_now=True)

    def __str__(self):
        return f"{self.start_date.strftime("%Y年%-m月%-d日")}～{self.end_date.strftime("%Y年%-m月%-d日")}"

    # バリデーション
    def clean(self):
        super().clean()
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "終了日は開始日より後の日付にしてください。"})

    class Meta:
        verbose_name = "年末年始休診"
        verbose_name_plural = "年末年始休診"


# =====================================================================================================
# 臨時休診日
# =====================================================================================================
class TempClosing(models.Model):
    date = models.DateField("臨時休診日", unique=True)
    closed_hours = models.CharField(
        "休診時間帯",
        max_length=10,
        choices=settings.CLOSED_TIME_CHOICES,
        default="all_day",
    )
    created_at = models.DateTimeField("変更日時", auto_now=True)

    def __str__(self):
        return f"{self.date.strftime("%Y年%-m月%-d日")} ({self.get_closed_hours_display()})"

    class Meta:
        verbose_name = "臨時休診日"
        verbose_name_plural = "臨時休診日"
