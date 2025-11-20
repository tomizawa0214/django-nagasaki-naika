from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View

from app.seo_meta import *


# =====================================================================================================
# マイページ
# =====================================================================================================
class MypageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # ユーザーを取得
        user_data = request.user 

        # ユーザーの名前を取得
        user_name = user_data.name

        # テンプレートを描画
        return render(request, "mypage.html", {**meta_mypage, "user_name": user_name})


# =====================================================================================================
# プライバシーポリシー
# =====================================================================================================
class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})
