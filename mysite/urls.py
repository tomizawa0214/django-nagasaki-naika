from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from sitemaps import StaticViewSitemap

admin.site.site_header = "長﨑医院ネット予約"
admin.site.index_title = "長﨑医院ネット予約"

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("management/", admin.site.urls),
    path("", include("app.accounts.urls")),
    path("", include("app.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

handler400 = "app.views.handler400_view"
handler403 = "app.views.handler403_view"
handler404 = "app.views.handler404_view"
handler500 = "app.views.handler500_view"
