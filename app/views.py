from django.shortcuts import render
from django.views.generic import View
from app.seo_meta import *


class PrivacyView(View):
    def get(self, request, *args, **kwargs):

        # テンプレートを描画
        return render(request, "privacy.html", {**meta_privacy})
