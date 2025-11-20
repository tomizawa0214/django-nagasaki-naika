from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "長﨑医院ネット予約"
admin.site.index_title = "長﨑医院ネット予約"

urlpatterns = [
    path("management/", admin.site.urls),
    path("", include("app.accounts.urls")),
    path("", include("app.urls")),
    path("accounts/", include("allauth.urls")),
]
