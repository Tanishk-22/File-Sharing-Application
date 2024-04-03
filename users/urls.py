from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import user_dashboard

urlpatterns = [
    path('', views.users_page, name='users_page'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='users_page'), name='logout'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
]