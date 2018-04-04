from django.urls import path

from . import views

app_name = 'campaigns'
urlpatterns = [
    path('', views.index, name='index'),
    path('add_campaign/', views.add_campaign, name='add_campaign'),
    path('<int:pk>/', views.CampaignView.as_view(), name='detail'),
    path('<int:campaign_id>/add_booking/', views.add_booking, name='add_booking'),
    path('booking/<int:pk>/', views.BookingView.as_view(), name='show_booking'),
    path('booking/<int:booking_id>/sheet/', views.show_booking_sheet, name='show_booking_sheet'),
]
