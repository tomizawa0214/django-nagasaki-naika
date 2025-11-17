from django.contrib import admin
from django.urls import path, include


admin.site.site_header = "長﨑医院Web予約システム"
admin.site.index_title = "長﨑医院Web予約システム"

urlpatterns = [
    path("management/", admin.site.urls),
    path("", include("app.urls")),
]
