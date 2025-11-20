from django.conf import settings


# 変数
site_name = "長﨑医院ネット予約"
separate = " | "

# ログイン
meta_login = {
    "meta_robots": "index,follow",
    "meta_title": f"{site_name}{separate}群馬県前橋市",
    "meta_description": "群馬県前橋市住吉町にある長﨑医院のネット予約ページです。インターネットから24時間いつでも簡単に予約ができます。",
    "url": f"{settings.BASE_URL}",
}

# パスワードリセット（メール入力）
meta_password_reset = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}password-reset/",
}

# パスワードリセット（メール認証）
meta_password_reset_verify = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット（メール認証）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}password-reset/verify/",
}

# パスワードリセット（パスワード再設定）
meta_password_reset_newpassword = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワード再設定{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}password-reset/new-password/",
}

# パスワードリセット（完了）
meta_password_reset_done = {
    "meta_robots": "noindex,follow",
    "meta_title": f"パスワードリセット完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}password-reset/done/",
}

# ご利用登録（入力）
meta_signup = {
    "meta_robots": "index,follow",
    "meta_title": f"利用登録{separate}{site_name}",
    "meta_description": "長﨑医院ネット予約を初めてご利用の方向けの利用登録ページです。簡単な登録で24時間いつでもインターネットから診察予約ができます。",
    "url": f"{settings.BASE_URL}signup/",
}

# ご利用登録（確認）
meta_signup_confirm = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録内容の確認{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}signup/confirm/",
}

# ご利用登録（メール認証）
meta_signup_verify = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録（メール認証）{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}signup/verify/",
}

# ご利用登録（完了）
meta_signup_done = {
    "meta_robots": "noindex,follow",
    "meta_title": f"利用登録完了{separate}{site_name}",
    "meta_description": "",
    "url": f"{settings.BASE_URL}signup/done/",
}

# プライバシーポリシー
meta_privacy = {
    "meta_robots": "index,follow",
    "meta_title": f"プライバシーポリシー{separate}{site_name}",
    "meta_description": "長﨑医院ネット予約でお預かりする個人情報の取り扱いについてご案内するプライバシーポリシーページです。",
    "url": f"{settings.BASE_URL}privacy/",
}
