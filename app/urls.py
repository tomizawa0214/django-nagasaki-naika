from django.urls import path
from app import views


urlpatterns = [
    path('mypage/', views.MypageView.as_view(), name='mypage'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]