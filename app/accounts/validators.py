import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomPasswordValidator:
    min_length = 8
    max_length = 20
    half_width_pattern = re.compile(r"^[ -~]+$")

    error_messages = {
        "min_length": _("8文字以上で入力してください。"),
        "max_length": _("20文字以内で入力してください。"),
        "letter_required": _("半角の英字を1文字以上含めてください。"),
        "digit_required": _("半角の数字を1文字以上含めてください。"),
        "half_width_only": _("使用できる文字は半角英数字と半角記号のみです。"),
    }

    def validate(self, password, user=None):
        errors = []

        if len(password) < self.min_length:
            errors.append(self.error_messages["min_length"])
        if len(password) > self.max_length:
            errors.append(self.error_messages["max_length"])
        if not self.half_width_pattern.fullmatch(password):
            errors.append(self.error_messages["half_width_only"])
        else:
            if not re.search(r"[A-Za-z]", password):
                errors.append(self.error_messages["letter_required"])
            if not re.search(r"\d", password):
                errors.append(self.error_messages["digit_required"])

        if errors:
            raise ValidationError(errors, code="password_format")

    def get_help_text(self):
        return _("8～20文字の半角英数字で入力してください。")
