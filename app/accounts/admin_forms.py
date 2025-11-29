from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


# =====================================================================================================
# 編集画面: パスワード
# =====================================================================================================
class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="パスワード")

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "family_name",
            "first_name",
            "phone",
            "birthdate",
            "gender",
            "card_number",
            "is_active",
            "is_staff",
        ]

    def clean_password(self):
        return self.initial.get("password")


# =====================================================================================================
# 新規画面: パスワード
# =====================================================================================================
class CustomUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label="パスワード", widget=forms.PasswordInput)
    password2 = forms.CharField(label="パスワード確認用", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "family_name",
            "first_name",
            "phone",
            "birthdate",
            "gender",
            "card_number",
            "is_active",
            "is_staff",
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません。")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password1"))
        if commit:
            user.save()
            self.save_m2m()
        return user
