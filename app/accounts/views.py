from allauth.account import views
from .forms import *


# =====================================================================================================
# ログイン
# =====================================================================================================
class LoginView(views.LoginView):
    template_name = "account/login.html"
    form_class = CustomLoginForm
    extra_context = {
        "meta_robots": "index,follow",
        "meta_title": "長﨑医院Web予約システム | 群馬県前橋市",
        "meta_description": "群馬県前橋市住吉町にある長﨑医院の診察Web予約システムページです。インターネットから24時間いつでも簡単に予約ができます。",
        "url": "https://yoyaku.nagasaki-naika.com",
    }
