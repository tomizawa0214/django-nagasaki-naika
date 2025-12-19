from django.contrib.sitemaps import Sitemap
from django.urls import reverse


# 静的ページのサイトマップ
class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["account_login", "account_signup", "privacy"]

    def location(self, item):
        return reverse(item)
