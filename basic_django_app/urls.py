from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-account/', views.create_account, name='create_account'),
    path('logout/', views.logout_view, name='logout'),
]
