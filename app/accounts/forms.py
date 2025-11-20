import datetime
import re
import unicodedata

from allauth.account.adapter import get_adapter
from allauth.account.forms import LoginForm, SignupForm
from allauth.account.internal import flows
from allauth.account.models import Login
from allauth.core import context
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm


# =====================================================================================================
# 初期設定
# =====================================================================================================

# 登録ユーザーを取得
User = get_user_model()


# =====================================================================================================
# ログインフォーム
# =====================================================================================================
class CustomLoginForm(LoginForm):

    # 属性値とエラーメッセージをカスタマイズ
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
                "invalid": "メールアドレスをもう一度ご確認ください。\n（全角文字や余分な空白がないかお確かめください）",
            }
        )

        # パスワード
        password = self.fields["password"]
        password.label = "パスワード"
        password.widget.attrs.update(
            {
                "class": "c-input",
                "id": "password",
                "placeholder": "パスワードを入力してください",
                "autocomplete": "current-password",
            }
        )
        password.error_messages.update(
            {
                "required": "パスワードを入力してください。",
            }
        )

    # ログイン処理のカスタマイズ（デフォルトの関数を継承）
    def _clean_with_password(self, credentials):

        # メールとパスワードを認証してユーザーを取得
        adapter = get_adapter(self.request)
        user = adapter.authenticate(self.request, **credentials)

        # ユーザーが存在 かつ is_active=False はアカウント無効
        if user and not user.is_active:
            raise adapter.validation_error("account_inactive")

        # ユーザーが存在 かつ is_active=True はログイン可にする（レート制限はチェック）
        if user:
            login = Login(user=user, email=credentials.get("email"))
            if flows.login.is_login_rate_limited(context.request, login):
                raise adapter.validation_error("too_many_login_attempts")
            self._login = login
            self.user = user

        # 認証に失敗はエラーメッセージ
        else:
            login_method = flows.login.derive_login_method(self.cleaned_data["login"])
            raise adapter.validation_error(f"{login_method.value}_password_mismatch")
        return self.cleaned_data


# =====================================================================================================
# パスワードリセットフォーム
# =====================================================================================================
class CustomPasswordResetForm(PasswordResetForm):

    # 登録メールアドレスのバリデーション
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("このメールアドレスは登録がありません。")
        return email


# =====================================================================================================
# 利用登録フォーム
# =====================================================================================================
class CustomSignupForm(SignupForm):

    # 追加フィールド
    user_family_name = forms.CharField(
        label="お名前 （姓）",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "id": "user-family-name",
                "placeholder": "長崎",
                "autocomplete": "family-name",
            }
        ),
        error_messages={"required": "名字を入力してください。"},
    )
    user_first_name = forms.CharField(
        label="お名前 （名）",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "id": "user-first-name",
                "placeholder": "太郎",
                "autocomplete": "given-name",
            }
        ),
        error_messages={"required": "お名前を入力してください。"},
    )
    phone = forms.CharField(
        label="電話番号",
        min_length=10,
        max_length=13,
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "type": "tel",
                "id": "phone",
                "inputmode": "numeric",
                "placeholder": "0272313274",
                "autocomplete": "tel-national",
            }
        ),
        error_messages={"required": "電話番号を入力してください。"},
    )
    birthdate = forms.DateField(
        label="生年月日",
        widget=forms.DateInput(
            attrs={
                "class": "c-text c-input",
                "type": "date",
                "id": "birthdate",
                "placeholder": "1970-01-01",
                "autocomplete": "bday",
                "max": datetime.date.today().isoformat(),
            }
        ),
        error_messages={"required": "生年月日を選択してください。"},
    )
    gender = forms.ChoiceField(
        label="性別",
        choices=settings.GENDER_CHOICES,
        widget=forms.widgets.RadioSelect,
        error_messages={"required": "性別を選択してください。"},
    )
    card_number = forms.CharField(
        label="診察券番号",
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "c-text c-input",
                "id": "card-number",
                "placeholder": "012345",
            }
        ),
        required=False,
    )
    privacy = forms.BooleanField(
        label="プライバシーポリシー",
        widget=forms.CheckboxInput(
            attrs={
                "class": "c-checkbox",
            }
        ),
        error_messages={"required": "プライバシーポリシーへの同意が必要です。チェックを入れてください。"},
    )

    # 電話番号のバリデーション
    def clean_phone(self):

        # 入力値を取得
        value = self.cleaned_data["phone"]

        # 半角に正規化
        normalized = unicodedata.normalize("NFKC", value)

        # 数字以外を除去
        phone_data = re.sub(r"\D", "", normalized)

        if not re.search(r"[0-9０-９]", value):
            raise forms.ValidationError("電話番号には数字を入力ください。")
        if len(phone_data) < 10:
            raise forms.ValidationError("電話番号は10桁以上で入力してください。")
        if len(phone_data) > 13:
            raise forms.ValidationError("電話番号は13桁以下で入力してください。")

        return phone_data

    # 生年月日のバリデーション
    def clean_birthdate(self):

        # 入力値を取得
        value = self.cleaned_data["birthdate"]

        # date型の場合はスルー
        if isinstance(value, datetime.date):
            return value

        # date型に変換
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise forms.ValidationError("生年月日は半角で1970-01-01の形式で入力してください。")

    # 診察券番号のバリデーション
    def clean_card_number(self):

        # 入力値を取得
        value = self.cleaned_data["card_number"]

        # 未入力ならそのまま空文字を返す
        if not value:
            return None

        # 半角に正規化
        normalized = unicodedata.normalize("NFKC", value)

        # 数字以外を除去
        card_number_data = re.sub(r"\D", "", normalized)

        if not re.search(r"[0-9０-９]", value):
            raise forms.ValidationError("診察券番号には数字を入力ください。")
        if len(card_number_data) > 10:
            raise forms.ValidationError("診察券番号は10桁以下で入力してください。")

        return card_number_data

    # 属性値とエラーメッセージをカスタマイズ
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # メールアドレス
        email = self.fields["email"]
        email.label = "メールアドレス"
        email.widget = forms.EmailInput(
            attrs={
                "class": "c-text c-input",
                "id": "email",
                "placeholder": "taro@example.jp",
                "autocomplete": "email",
            }
        )
        email.error_messages.update(
            {
                "required": "メールアドレスを入力してください。",
                "invalid": "メールアドレスをもう一度ご確認ください。\n・全角文字や余分な空白がないかお確かめください\n・古い形式のアドレスはご利用いただけない場合があります。別のメールアドレスをお試しください",
            }
        )

        # パスワード
        password = self.fields["password1"]
        password.label = "パスワード"
        password.widget.attrs.update(
            {
                "class": "c-input",
                "id": "password",
                "placeholder": "パスワードを入力してください",
            }
        )
        password.error_messages.update(
            {
                "required": "パスワードを入力してください。",
            }
        )
