from datetime import date, timedelta
import mimetypes

from django.contrib.auth.decorators import login_required
from django.contrib.auth import mixins
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views import generic

from .models import BookingSheet, Campaign
from .forms import BookingSheetForm, CampaignForm

class CampaignView(mixins.LoginRequiredMixin, generic.DetailView):
    model = Campaign

class BookingView(mixins.LoginRequiredMixin, generic.DetailView):
    model = BookingSheet

@login_required
def index(request):
    campaigns = Campaign.objects.all()
    active_campaigns = []
    upcoming_campaigns = []
    past_campaigns = []
    for campaign in campaigns:
        start_date = campaign.get_start_date()
        end_date = campaign.get_end_date()
        if campaign.is_active():
            active_campaigns.append(campaign)
        elif end_date != None and end_date < date.today():
            past_campaigns.append(campaign)
        elif start_date != None and start_date - date.today() < timedelta(weeks=1):
            upcoming_campaigns.append(campaign)

    context = {
        'active_campaigns': active_campaigns,
        'upcoming_campaigns': upcoming_campaigns,
        'past_campaigns': past_campaigns,
    }
    return render(request, 'campaigns/index.html', context)

@login_required
def add_booking(request, campaign_id):
    if request.method == "POST":
        campaign = Campaign.objects.get(id=campaign_id)
        booking = BookingSheet(campaign=campaign)
        form = BookingSheetForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            booking = form.save()
            return redirect('campaigns:detail', campaign_id)
        else:
            context = {
                'form': form,
                'campaign': campaign,
            }
            return render(request, 'campaigns/add_booking.html', context)

    else:
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        form = BookingSheetForm()
        context = {
            'form': form,
            'campaign': campaign,
        }
        return render(request, 'campaigns/add_booking.html', context)

@login_required
def add_campaign(request):
    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save()
            return redirect("campaigns:add_booking", campaign_id=campaign.id)
        else:
            context = {
                'form': form,
                'campaign': campaign,
            }
            return render(request, 'campaigns/add_campaign.html', context)

    else:
        form = CampaignForm()
        context = {
            'form': form,
        }
        return render(request, 'campaigns/add_campaign.html', context)

@login_required
def download_booking_sheet(request, booking_id):
    booking = get_object_or_404(BookingSheet, pk=booking_id)
    mimetype = mimetypes.guess_type(booking.material.url)[0]
    response = HttpResponse(booking.material, content_type=mimetype)
    response['Content-Disposition'] = 'filename="' + booking.material.name + '"\''
    return response
