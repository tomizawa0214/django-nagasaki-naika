from django.conf import settings


# 変数
site_name = "長﨑医院ネット予約"
separate = " | "

# ログイン
meta_login = {
    "meta_robots": "index,follow",
    "meta_title": f"{site_name}{separate}群馬県前橋市",
    "meta_description": "群馬県前橋市住吉町にある長﨑医院のネット予約ページです。インターネットから24時間いつでも簡単に予約ができます。",
    "url": f"{settings.BASE_URL}/",
}

# パスワードリセット（メール入力）
meta_password_reset = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/password-reset/",
}

# パスワードリセット（メール認証）
meta_password_reset_verify = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット（メール認証）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/password-reset/verify/",
}

# パスワードリセット（パスワード再設定）
meta_password_reset_newpassword = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワード再設定{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/password-reset/new-password/",
}

# パスワードリセット（完了）
meta_password_reset_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/password-reset/complete/",
}

# ご利用登録（入力）
meta_signup = {
    "meta_robots": "index,follow",
    "meta_title": f"利用登録{separate}{site_name}",
    "meta_description": "長﨑医院ネット予約を初めてご利用の方向けの利用登録ページです。簡単な登録で24時間いつでもインターネットから診察予約ができます。",
    "url": f"{settings.BASE_URL}/signup/",
}

# ご利用登録（確認）
meta_signup_confirm = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録内容の確認{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/signup/confirm/",
}

# ご利用登録（メール認証）
meta_signup_verify = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録（メール認証）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/signup/verify/",
}

# ご利用登録（完了）
meta_signup_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/signup/complete/",
}
meta_signup_failed = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録失敗{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/signup/complete/",
}

# マイページ
meta_mypage = {
    "meta_robots": "noindex,follow",
    "meta_title": f"マイページ{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/",
}

# 診察予約（初診 / 再診）
meta_appointment = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/",
}

# 診察予約（問診票）
meta_appointment_questionnaire = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約（問診票の入力）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/questionnaire/",
}

# 診察予約（日時選択）
meta_appointment_datetime = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約（日時の選択）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/datetime/",
}

# 診察予約（連絡先入力）
meta_appointment_contact = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約（連絡先の入力）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/contact/",
}

# 診察予約（確認）
meta_appointment_confirm = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約内容の確認{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/confirm/",
}

# 診察予約（完了）
meta_appointment_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"診察予約完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/appointment/complete/",
}

# 予約の変更（予約確認）
meta_appointment_detail = {
    "meta_robots": "noindex,follow",
    "meta_title": f"予約内容の確認{separate}{site_name}",
    "meta_description": "",
}

# 予約の変更（連絡先の変更）
meta_appointment_edit_contact = {
    "meta_robots": "noindex,follow",
    "meta_title": f"連絡先の変更{separate}{site_name}",
    "meta_description": "",
}

# 予約の変更（変更確認）
meta_appointment_edit_contact_confirm = {
    "meta_robots": "noindex,follow",
    "meta_title": f"連絡先の変更内容の確認{separate}{site_name}",
    "meta_description": "",
}

# 予約の変更（完了）
meta_appointment_edit_contact_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"連絡先の変更完了{separate}{site_name}",
    "meta_description": "",
}

# 予約の変更（日時変更）
meta_appointment_edit_datetime = {
    "meta_robots": "noindex,follow",
    "meta_title": f"予約日時の変更{separate}{site_name}",
    "meta_description": "",
}

# 予約の変更（完了）
meta_appointment_edit_datetime_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"予約日時の変更完了{separate}{site_name}",
    "meta_description": "",
}

# パスワード変更（入力）
meta_password_change = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワード変更{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/password/",
}

# パスワード変更（完了）
meta_password_change_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワード変更完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/password/complete/",
}

# メールアドレス変更（入力）
meta_email_change = {
    "meta_robots": "noindex,follow",
    "meta_title": f"メールアドレス変更{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/email/",
}

# メールアドレス変更（メール認証）
meta_email_change_verify = {
    "meta_robots": "noindex,follow",
    "meta_title": f"メールアドレス変更（メール認証）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/email/verify/",
}

# メールアドレス変更（完了）
meta_email_change_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"メールアドレス変更完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/email/complete/",
}
meta_email_change_failed = {
    "meta_robots": "noindex,follow",
    "meta_title": f"メールアドレス変更失敗{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/email/complete/",
}

# 電話番号変更（入力）
meta_phone_change = {
    "meta_robots": "noindex,follow",
    "meta_title": f"電話番号変更{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/phone/",
}

# 電話番号変更（完了）
meta_phone_change_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"電話番号変更完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/phone/complete/",
}

# 退会（確認）
meta_withdraw = {
    "meta_robots": "noindex,follow",
    "meta_title": f"退会確認{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/withdraw/",
}

# 退会（完了）
meta_withdraw_complete = {
    "meta_robots": "noindex,follow",
    "meta_title": f"退会完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/mypage/withdraw/complete/",
}

# ログアウト
meta_logout = {
    "meta_robots": "noindex,follow",
    "meta_title": f"ログアウト{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}/logout/",
}

# プライバシーポリシー
meta_privacy = {
    "meta_robots": "index,follow",
    "meta_title": f"プライバシーポリシー{separate}{site_name}",
    "meta_description": "長﨑医院ネット予約でお預かりする個人情報の取り扱いについてご案内するプライバシーポリシーページです。",
    "url": f"{settings.BASE_URL}/privacy/",
}
