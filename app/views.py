from django.conf import settings
from django.shortcuts import render
from django.views.generic import View


class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # メタタグ
        extra_context = {
            "meta_robots": "index,follow",
            "meta_title": "プライバシーポリシー | 長﨑医院ネット予約",
            "meta_description": "長﨑医院ネット予約でお預かりする個人情報の取り扱いについてご案内するプライバシーポリシーページです。",
            "url": f"{settings.BASE_URL}privacy/",
        }

        # テンプレートを描画
        return render(request, "privacy.html", {"extra_context": extra_context})
