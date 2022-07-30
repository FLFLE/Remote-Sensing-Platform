from django.urls import path
from webapps.user import views

urlpatterns = [
    path('',views.UserView.as_view()),
    path('vtf/',views.SendVertificationCode.as_view()),
    path('password/',views.PasswordView.as_view())
]