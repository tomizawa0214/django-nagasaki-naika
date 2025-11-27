from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


# =====================================================================================================
# 休診日
# =====================================================================================================
class RegularClosing(models.Model):
    weekday = models.CharField("休診の曜日", choices=settings.CLOSED_WEEKDAY_CHOICES, max_length=10)
    closed_hours = models.CharField(
        "休診の時間帯",
        max_length=10,
        choices=settings.CLOSED_TIME_CHOICES,
        default="both",
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
        return f"{self.start_date.strftime("%Y年%m月%d日(%a)")}～{self.end_date.strftime("%Y年%m月%d日(%a)")}"
    
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
        return f"{self.start_date.strftime("%Y年%m月%d日(%a)")}～{self.end_date.strftime("%Y年%m月%d日(%a)")}"
    
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
    date = models.DateField("臨時休診日")
    closed_hours = models.CharField(
        "休診時間帯",
        max_length=10,
        choices=settings.CLOSED_TIME_CHOICES,
        default="both",
    )
    created_at = models.DateTimeField("変更日時", auto_now=True)

    def __str__(self):
        return f"{self.date.strftime("%Y年%m月%d日(%a)")} ({self.get_closed_hours_display()})"

    class Meta:
        verbose_name = "臨時休診日"
        verbose_name_plural = "臨時休診日"
