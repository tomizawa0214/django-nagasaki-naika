from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


# =====================================================================================================
# ユーザーを作成
# =====================================================================================================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# =====================================================================================================
# カスタムユーザー
# =====================================================================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    family_name = models.CharField("お名前 （姓）", max_length=100)
    first_name = models.CharField("お名前 （名）", max_length=100)
    email = models.EmailField("メールアドレス", max_length=256, unique=True)
    phone = models.CharField("電話番号", max_length=13)
    birthdate = models.DateField("生年月日")
    gender = models.CharField("性別", max_length=10, choices=settings.GENDER_CHOICES)
    card_number = models.CharField("診察券番号", max_length=10, blank=True, null=True)
    is_active = models.BooleanField(
        "ログイン権限",
        default=True,
        help_text=("※ネット予約にログインできるかを指定します。<br>" "※退会の場合はチェックを解除します。"),
    )
    is_staff = models.BooleanField(
        "管理画面のアクセス権限",
        default=False,
        help_text="※この管理画面にログインできるかを指定します。<br>"
        "※ログイン権限にもチェックを入れることが必須です。",
    )
    created_at = models.DateTimeField("登録日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    # デフォルトのマネージャーをカスタム実装に差し替え
    objects = CustomUserManager()

    # メールアドレス認証に対応
    USERNAME_FIELD = "email"

    # メールアドレスフィールドの指定
    EMAIL_FIELD = "email"

    # ユーザー作成コマンドにおけるメールアドレス以外の必須項目の指定
    REQUIRED_FIELDS = ["family_name", "first_name", "phone", "birthdate", "gender"]

    # 管理画面の表示名
    class Meta:
        verbose_name = "登録ユーザー"
        verbose_name_plural = "登録ユーザー"

    # 編集画面の表示名
    def __str__(self):
        return f"{self.family_name} {self.first_name}"

    # メールアドレスを正規化
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
