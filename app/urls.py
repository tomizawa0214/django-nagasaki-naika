from django.urls import path
from app import views


urlpatterns = [
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]