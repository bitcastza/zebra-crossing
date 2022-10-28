from django.urls import path

from . import views

app_name = "campaigns"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/schedule/save", views.save_schedule, name="save_schedule"),
    path("add_campaign/", views.CampaignCreate.as_view(), name="add_campaign"),
    path("<int:pk>/", views.CampaignView.as_view(), name="detail"),
    path(
        "<int:campaign_id>/add_booking/",
        views.BookingSheetCreate.as_view(),
        name="add_booking",
    ),
    path(
        "<int:campaign_id>/add_material/",
        views.MaterialCreate.as_view(),
        name="add_material",
    ),
    path("booking/<int:pk>/", views.BookingView.as_view(), name="show_booking"),
    path(
        "booking/<int:booking_id>/download",
        views.download_booking_sheet,
        name="download_booking_sheet",
    ),
    path(
        "material/<int:material_id>/download",
        views.download_material,
        name="download_material",
    ),
]
