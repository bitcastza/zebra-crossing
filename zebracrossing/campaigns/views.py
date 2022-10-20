from datetime import datetime, date, timedelta
import mimetypes

from django.contrib.auth.decorators import login_required
from django.contrib.auth import mixins
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse

from .models import BookingSheet, Campaign, Material, TimeSlot, BookedDay
from .forms import BookingSheetForm, CampaignForm, MaterialForm
from django.core import serializers
import json


class CampaignView(mixins.LoginRequiredMixin, DetailView):
    model = Campaign

    def get_context_data(self, **kwargs):

        sheet = BookingSheet.objects.filter(campaign=self.get_object())[0]
        table_data = BookedDay.objects.filter(bookingsheet=sheet)
        all_campaign_slots = TimeSlot.objects.all()
        bookingsheet = BookingSheet.objects.filter(campaign=self.get_object())

        for date in bookingsheet:
            start_date = datetime.strptime(str(date.start_date), "%Y-%m-%d")
            end_date = datetime.strptime(str(date.end_date), "%Y-%m-%d")

        all_campaign_dates = [
            start_date + timedelta(days=x)
            for x in range((end_date - start_date).days + 1)
        ]

        booked_info = {}
        for data in table_data:
            booked_info[datetime.strftime(data.date, "%Y-%m-%d")] = str(data.timeslot)

        booking_set = {}
        for date in all_campaign_dates:
            day_slots = []
            for slot in all_campaign_slots:
                day_slots.append(
                    {
                        "slot_id": slot.id,
                        "booked": True
                        if (datetime.strftime(date, "%Y-%m-%d"), str(slot))
                        in booked_info.items()
                        else False,
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
        context["booked_day"] = BookedDay.objects.all()
        context["array"] = json.dumps(booked_view)
        # add this below and return the bookinghsheet id from the javascript side
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


def create_date_from_table_header(date):
    result = date[str(date).find("(") + 1 : str(date).find(")")]
    day = result.split("/")[0]
    month = result.split("/")[1]
    year = str(datetime.today().year)
    date_object = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
    return date_object


def save_to_table(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["GET"])

    bookingsheet_id = None
    time = None

    if bool(request.POST.get("arr")) == True:
        try:
            for data in json.loads(request.POST.get("arr")):
                time = TimeSlot.objects.raw(
                    "SELECT * FROM campaigns_timeslot where time=%s",
                    [data["slot_time"]],
                )[0]
                bookingsheet_id = data["bookingsheet_id"]
                booking = BookedDay(
                    date=create_date_from_table_header(data["date"]),
                    timeslot=time,
                    bookingsheet=BookingSheet.objects.get(id=bookingsheet_id),
                )

                booking.save()
        except TypeError:
            pass
    return HttpResponse(status=200)
