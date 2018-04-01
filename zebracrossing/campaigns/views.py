from datetime import date

from django.shortcuts import get_object_or_404, render, redirect

from .models import BookingSheet, Campaign
from .forms import BookingSheetForm

def index(request):
    campaigns = Campaign.objects.all()
    active_campaigns = []
    upcoming_campaigns = []
    past_campaigns = []
    for campaign in campaigns:
        start_date = campaign.get_start_date()
        if campaign.is_active():
            active_campaigns.append(campaign)
        elif start_date != None and start_date - date.today() < 7:
            upcoming_campaigns.append(campaign)
        elif start_date != None:
            past_campaigns.append(campaign)

    context = {
        'active_campaigns': active_campaigns,
        'upcoming_campaigns': upcoming_campaigns,
        'past_campaigns': past_campaigns,
    }
    return render(request, 'campaigns/index.html', context)

def detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    booking_sheets = BookingSheet.objects.filter(campaign=campaign_id)
    context = {
        'campaign': campaign,
        'booking_sheets': booking_sheets,
    }
    return render(request, 'campaigns/detail.html', context)

def add_booking(request, campaign_id):
    if request.method == "POST":
        campaign = Campaign.objects.get(id=campaign_id)
        booking = BookingSheet(campaign=campaign)
        form = BookingSheetForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            booking = form.save()
            return redirect('campaigns:detail', campaign_id=campaign_id)
        else:
            context = {
                'form': form,
                'campaign': campaign,
            }
            return render(request, 'campaigns/addbooking.html', context)

    else:
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        form = BookingSheetForm()
        context = {
            'form': form,
            'campaign': campaign,
        }
        return render(request, 'campaigns/addbooking.html', context)
