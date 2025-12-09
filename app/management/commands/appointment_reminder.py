import datetime
import email.utils
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from app.models import Appointment

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "翌日予約者へのリマインドメール送信"

    def handle(self, *args, **options):

        # 本日
        today = datetime.date.today()

        # 明日
        tomorrow = today + timedelta(days=1)

        # 明日の予約データを取得
        appointment_data = Appointment.objects.select_related("user").filter(appointment_dt__date=tomorrow)

        # 明日の予約が無い場合
        if not appointment_data.exists():
            logger.exception("翌日の予約なし")
            return

        # 明日の予約データごとに処理
        for appointment in appointment_data:

            # 送信先メールアドレス
            user_email = appointment.email or appointment.user.email

            # メールに使用する変数
            user = appointment.user
            context = {
                "appointment_dt": timezone.localtime(appointment.appointment_dt),
                "user_name": f"{appointment.family_name or getattr(user, "family_name", "")} {appointment.first_name or getattr(user, "first_name", "")}",
                "user_email": appointment.email or getattr(user, "email", ""),
                "user_phone": appointment.phone or getattr(user, "phone", ""),
                "birthdate": appointment.birthdate or getattr(user, "birthdate", ""),
                "gender": appointment.get_gender_display() or (user.get_gender_display() if user else ""),
                "card_number": appointment.card_number or getattr(user, "card_number", ""),
                "created_at": timezone.localtime(appointment.created_at),
            }

            # メール設定
            subject = render_to_string("mail_template/subject/appointment_reminder.txt", context)
            message = render_to_string("mail_template/message/appointment_reminder.txt", context)
            from_email = email.utils.formataddr((settings.SITE_NAME, settings.EMAIL_HOST_USER))
            to_list = [user_email]

            # メール送信
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=to_list,
                )
            except Exception as exc:
                logger.exception("reminder email failed: %s", exc)
