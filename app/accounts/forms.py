from allauth.account.forms import LoginForm
from django import forms
from django.core.validators import RegexValidator

# =====================================================================================================
# バリデーション
# =====================================================================================================
password_validator = RegexValidator(
    regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$",
    message="8～20文字で、半角の英字と数字を1文字以上ずつ含めてください。",
)


# =====================================================================================================
# ログインフォーム
# =====================================================================================================
class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # メールアドレス
        login = self.fields["login"]
        login.label = "メールアドレス"
        login.widget = forms.EmailInput(
            attrs={
                "class": "c-text c-input",
                "id": "email",
                "placeholder": "taro@example.jp",
                "autocomplete": "email",
            }
        )
        login.error_messages.update(
            {
                "required": "メールアドレスを入力してください。",
                "invalid": "メールアドレスの形式が正しくありません。",
            }
        )

        # パスワード
        password = self.fields["password"]
        password.label = "パスワード"
        password.widget.attrs.update(
            {
                "class": "c-input",
                "id": "password",
                "placeholder": "パスワードを入力してください。",
                "autocomplete": "current-password",
            }
        )
        password.error_messages.update(
            {
                "required": "パスワードを入力してください。",
            }
        )
