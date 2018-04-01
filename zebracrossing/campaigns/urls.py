from django.urls import path

from . import views

app_name = 'campaigns'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:campaign_id>/', views.detail, name='detail'),
    path('<int:campaign_id>/add_booking/', views.add_booking, name='add_booking'),
    path('booking/<int:booking_id>/', views.show_booking, name='show_booking'),
]
