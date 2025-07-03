from django.contrib import admin
from django.urls import path, include
from quotes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.random_quote, name='random_quote'),
    path('add/', views.add_quote, name='add_quote'),
    path('vote/', views.vote_quote, name='vote_quote'),
    path('top_ten/', views.top_ten, name='top_ten'),
]
