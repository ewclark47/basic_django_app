from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('create-account/', views.create_account, name='create_account'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('api/tags/', api.tag_count_api, name='api_tag_count'),
    path('api/authors/', api.author_count_api, name='api_author_count'),
]
