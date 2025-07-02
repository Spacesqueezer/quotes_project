from django.urls import path
from . import views

urlpatterns = [
	path('add/', views.add_quote, name='add_quote'),
]
