from datetime import datetime, date, timedelta
import mimetypes
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth import mixins
from django.core import serializers
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse

from .models import BookingSheet, Campaign, Material, TimeSlot, BookedDay
from .forms import BookingSheetForm, CampaignForm, MaterialForm


class CampaignView(mixins.LoginRequiredMixin, DetailView):
    model = Campaign

    def get_context_data(self, **kwargs):
        sheet = BookingSheet.objects.filter(campaign=self.get_object())[0]
        table_data = BookedDay.objects.filter(bookingsheet=sheet)
        all_campaign_slots = TimeSlot.objects.all()
        bookingsheet = BookingSheet.objects.filter(campaign=self.get_object())

        all_campaign_dates = []
        for sheet in bookingsheet:
            start_date = sheet.start_date
            end_date = sheet.end_date

            all_campaign_dates = [
                start_date + timedelta(days=x)
                for x in range((end_date - start_date).days + 1)
            ]

        booked_info = {}
        for data in table_data:
            booked_info[data.date] = data.timeslot

        booking_set = {}
        for date in all_campaign_dates:
            day_slots = []
            for slot in all_campaign_slots:
                day_slots.append(
                    {
                        "slot_id": slot.id,
                        "booked": slot in booked_info.items(),
                    }
                )
            booking_set[date] = day_slots

        booked_view = []
        for date, slots in booking_set.items():
            booked_day = []
            for slot in slots:
                booked_day.append(slot["booked"])
            booked_view.append(booked_day)

        context = super().get_context_data(**kwargs)
        context["timeslots"] = serializers.serialize("json", TimeSlot.objects.all())
        context["booked_day"] = table_data
        # TODO: replace schedule object with:
        # schedule = {
        #     booking_sheet: 1,
        #     bookings: [
        #       ...
        #       {
        #         slot_time: '17:20',
        #         date: '2022-10-01'
        #       }
        #     ]
        context["schedule"] = json.dumps(booked_view)
        print(context["schedule"])
        context["bookingsheet"] = sheet
        return context


class BookingView(mixins.LoginRequiredMixin, DetailView):
    model = BookingSheet


@login_required
def index(request):
    campaigns = Campaign.objects.all()
    active_campaigns = []
    upcoming_campaigns = []
    past_campaigns = []
    for campaign in campaigns:
        start_date = campaign.start_date
        end_date = campaign.end_date
        if campaign.is_active():
            active_campaigns.append(campaign)
        elif end_date != None and end_date < date.today():
            past_campaigns.append(campaign)
        elif start_date != None and start_date - date.today() < timedelta(weeks=1):
            upcoming_campaigns.append(campaign)

    context = {
        "active_campaigns": active_campaigns,
        "upcoming_campaigns": upcoming_campaigns,
        "past_campaigns": past_campaigns,
    }
    return render(request, "campaigns/index.html", context)


class BookingSheetCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = "campaigns/add_update_object.html"
    form_class = BookingSheetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Upload Booking Sheet"
        context["url"] = reverse(
            "campaigns:add_booking", kwargs={"campaign_id": self.kwargs["campaign_id"]}
        )
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["campaign"] = Campaign.objects.get(id=self.kwargs["campaign_id"])
        return initial

    def get_success_url(self):
        return reverse("campaigns:detail", kwargs={"pk": self.kwargs["campaign_id"]})


class MaterialCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = "campaigns/add_update_object.html"
    form_class = MaterialForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Upload Material"
        context["url"] = reverse(
            "campaigns:add_material", kwargs={"campaign_id": self.kwargs["campaign_id"]}
        )
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["campaign"] = Campaign.objects.get(id=self.kwargs["campaign_id"])
        return initial

    def get_success_url(self):
        return reverse("campaigns:detail", kwargs={"pk": self.kwargs["campaign_id"]})


class CampaignCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = "campaigns/add_update_object.html"
    form_class = CampaignForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Campaign"
        context["url"] = reverse("campaigns:add_campaign")
        return context

    def get_success_url(self):
        return reverse("campaigns:add_booking", kwargs={"campaign_id": self.object.id})


@login_required
def download_booking_sheet(request, booking_id):
    booking = get_object_or_404(BookingSheet, pk=booking_id)
    return download_item(request, booking.booking_sheet)


@login_required
def download_material(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    return download_item(request, material.material)


@login_required
def download_item(request, item):
    mimetype = mimetypes.guess_type(item.url)[0]
    response = HttpResponse(item, content_type=mimetype)
    response["Content-Disposition"] = f'filename="{item.name}"'
    return response


@login_required
def save_schedule(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    time = None

    if request.POST.get("bookings") is not None:
        # TODO: replace schedule object with:
        # schedule = {
        #     booking-sheet: 1,
        #     bookings: [
        #       ...
        #       {
        #         slot-time: '17:20',
        #         date: '2022-10-01'
        #       }
        #     ]
        booking_sheet_id = request.POST.get("booking-sheet")
        booking_sheet = BookingSheet.objects.get(id=booking_sheet_id)
        bookings = request.POST.get("bookings")
        for booking in bookings:
            time = TimeSlot.objects.filter(time=booking["slot-time"]).first()
            booking = BookedDay(
                date=datetime.date.fromisoformat(booking["date"]),
                timeslot=time,
                bookingsheet=booking_sheet,
            )
            booking.save()
    else:
        return HttpResponseBadRequest("No data passed to be processed and saved.")
    return HttpResponse(status=200)
