from django.urls import path
from . import views

urlpatterns = [
	path('add/', views.add_quote, name='add_quote'),
	# path('vote/', views.vote_quote, name='vote_quote'),
]
