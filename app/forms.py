import datetime
from datetime import timedelta

from django import forms
from django.conf import settings
from .accounts.forms import *


# =====================================================================================================
# 診察予約フォーム（初診 / 再診）
# =====================================================================================================
class AppointmentVisitForm(forms.Form):
    visit = forms.ChoiceField(
        label="初診 / 再診",
        choices=settings.VISIT_CHOICES,
        widget=forms.widgets.RadioSelect,
        initial="first",
        error_messages={"required": "初診または再診を選択してください。"},
    )


# =====================================================================================================
# 問診票フォーム
# =====================================================================================================
class AppointmentQuestionnaireForm(forms.Form):
    symptom = forms.MultipleChoiceField(
        label="本日はどうなさいましたか？",
        choices=settings.SYMTOM_CHOICES,
        widget=forms.widgets.CheckboxSelectMultiple,
        error_messages={"required": "当てはまるものを選択してください。"},
    )
    symptom_other = forms.CharField(
        label="その他",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input js-symptom-other-field",
                "placeholder": "その他の症状を具体的にご記入ください",
            }
        ),
        required=False,
    )
    symptom_start = forms.ChoiceField(
        label="症状はいつ頃からありますか？",
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        error_messages={"required": "当てはまるものを選択してください。"},
    )
    medical_history = forms.ChoiceField(
        label="過去に大きな病気で治療や手術を受けられたことはありますか？",
        choices=settings.YES_OR_NO_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    has_medical_history = forms.CharField(
        label="ある",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input js-has-medical-history-field",
                "placeholder": "具体的にご記入ください",
            }
        ),
        required=False,
    )
    under_treatment = forms.ChoiceField(
        label="現在、治療中の病気はありますか？",
        choices=settings.YES_OR_NO_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    has_under_treatment = forms.CharField(
        label="ある",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input js-has-under-treatment-field",
                "placeholder": "具体的にご記入ください",
            }
        ),
        required=False,
    )
    current_medication = forms.ChoiceField(
        label="現在、飲んでいるお薬はありますか？",
        choices=settings.YES_OR_NO_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    has_current_medication = forms.CharField(
        label="ある",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input js-has-current-medication-field",
                "placeholder": "具体的にご記入ください",
            }
        ),
        required=False,
    )
    smoking = forms.ChoiceField(
        label="煙草",
        choices=settings.SMOKING_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    has_smoking_per_day = forms.ChoiceField(
        label="1日の喫煙本数",
        choices=settings.SMOKING_PER_DAY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        required=False,
    )
    has_smoking_years = forms.ChoiceField(
        label="喫煙の期間",
        choices=settings.YEARS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        required=False,
    )
    has_quit_smoking_years = forms.ChoiceField(
        label="禁煙の期間",
        choices=settings.QUIT_SMOKING_YEARS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        required=False,
    )
    has_until_smoking_years = forms.ChoiceField(
        label="禁煙するまでの喫煙期間",
        choices=settings.YEARS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        required=False,
    )
    alcohol = forms.ChoiceField(
        label="飲酒",
        choices=settings.ALCOHOL_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    alcohol_per_week = forms.ChoiceField(
        label="1週間の飲酒の頻度",
        choices=settings.ALCOHOL_PER_WEEK_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "c-text c-select",
            },
        ),
        initial="",
        required=False,
    )
    alcohol_type = forms.CharField(
        label="飲酒の種類",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "id": "alcohol-type",
                "placeholder": "ビール、日本酒など",
            }
        ),
        required=False,
    )
    alcohol_amount = forms.CharField(
        label="飲酒の量",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "id": "alcohol-amount",
                "placeholder": "ビール500ml缶1本、日本酒1合など",
            }
        ),
        required=False,
    )
    allergy = forms.ChoiceField(
        label="お薬・食べ物のアレルギーはありますか？",
        choices=settings.YES_OR_NO_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
    )
    has_allergy = forms.CharField(
        label="ある",
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input js-has-allergy-field",
                "placeholder": "具体的にご記入ください",
            }
        ),
        required=False,
    )
    pregnancy = forms.ChoiceField(
        label="現在、妊娠中あるいは妊娠の可能性、または授乳中ですか？",
        choices=settings.PREGNANCY_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "いずれかを選択してください。"},
        initial="no",
    )
    especially = forms.CharField(
        label="特に調べてほしいこと、検査、治療がありましたらご記入ください",
        widget=forms.Textarea(
            attrs={
                "class": "c-text c-textarea",
                "id": "especially",
                "placeholder": "ご希望がありましたら記入してください",
            }
        ),
        required=False,
    )

    # 「症状はいつ頃からありますか？」の選択肢を動的に生成
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 今日
        today = datetime.date.today()

        # 昨日
        yesterday = today - timedelta(days=1)

        # 3日前
        ago_3days = today - timedelta(days=3)

        # 6日前
        ago_6days = today - timedelta(days=6)

        # 1週間以上前
        gt_7days = today - timedelta(days=7)

        choices = (
            ("", "選択してください"),
            (today, "今日から"),
            (yesterday, "昨日から"),
            (ago_3days, "2〜3日前から"),
            (ago_6days, "4〜6日前から"),
            (gt_7days, "1週間以上前から"),
        )
        self.fields["symptom_start"].choices = choices
        self.fields["symptom_start"].initial = ""


# =====================================================================================================
# 日時選択フォーム
# =====================================================================================================
class AppointmentDatetimeForm(forms.Form):
    appointment_dt = forms.ChoiceField(
        label="来院日時",
        choices=(),
        widget=forms.widgets.RadioSelect(
            attrs={
                "class": "c-calendar__status-radio",
            },
        ),
        error_messages={
            "required": "予約日時を選択してください。",
            "invalid_choice": "ご希望の日時ではご予約をお取りできませんでした。\n別の日時でもう一度お試しください。",
        },
    )


# =====================================================================================================
# 連絡先フォーム
# =====================================================================================================
class AppointmentContactForm(BaseContactFieldsMixin):
    email = forms.EmailField(
        label="メールアドレス",
        max_length=100,
        widget=forms.EmailInput(
            attrs={
                "class": "c-text c-input",
                "id": "email",
                "placeholder": "taro@example.jp",
                "autocomplete": "email",
            }
        ),
        error_messages={
            "required": "メールアドレスを入力してください。",
            "invalid": "メールアドレスをもう一度ご確認ください。\n・全角文字や余分な空白がないかお確かめください\n・古い形式のアドレスはご利用いただけない場合があります。別のメールアドレスをお試しください",
        },
    )
