from django.urls import path
from webapps.history import views

urlpatterns = [
    path("", views.HistoryView.as_view()),
    path('usage/', views.UsageView.as_view()),
    path('times/', views.UsageView.as_view())
]
