from django import forms
from django.conf import settings
from django.contrib.admin.helpers import ActionForm

from .models import Questionnaire


# =====================================================================================================
# 編集画面: 問診票の症状
# =====================================================================================================
class QuestionnaireAdminForm(forms.ModelForm):
    symptom = forms.MultipleChoiceField(
        label="症状",
        choices=settings.SYMTOM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Questionnaire
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.symptom:
            self.initial["symptom"] = self.instance.symptom

    def clean_symptom(self):
        return self.cleaned_data["symptom"]


# =====================================================================================================
# 一覧画面: 問診票の実行ドロップダウン路の初期値をPDFダウンロードにする
# =====================================================================================================
class QuestionnaireActionForm(ActionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "action" in self.fields:
            self.fields["action"].initial = "download_pdf"
