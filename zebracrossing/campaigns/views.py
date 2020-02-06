from datetime import date, timedelta
import mimetypes

from django.contrib.auth.decorators import login_required
from django.contrib.auth import mixins
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy

from zebracrossing.forms import CalendarWidget, FileWidget
from .models import BookingSheet, Campaign, Material
from .forms import BookingSheetForm, CampaignForm, MaterialForm

class CampaignView(mixins.LoginRequiredMixin, DetailView):
    model = Campaign

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
        'active_campaigns': active_campaigns,
        'upcoming_campaigns': upcoming_campaigns,
        'past_campaigns': past_campaigns,
    }
    return render(request, 'campaigns/index.html', context)

class BookingSheetCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = 'campaigns/add_update_object.html'
    form_class = BookingSheetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload Booking Sheet'
        context['url'] = reverse('campaigns:add_booking', args=[self.kwargs['campaign_id']])
        return context

    def get_success_url(self):
        return redirect('campaigns:detail', self.kwargs['campaign_id'])

class MaterialCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = 'campaigns/add_update_object.html'
    form_class = MaterialForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload Material'
        context['url'] = reverse('campaigns:add_material', args=[self.kwargs['campaign_id']])
        return context

    def get_success_url(self):
        return redirect('campaigns:detail', self.kwargs['campaign_id'])

class CampaignCreate(mixins.LoginRequiredMixin, CreateView):
    template_name = 'campaigns/add_update_object.html'
    form_class = CampaignForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Campaign'
        context['url'] = reverse('campaigns:add_campaign')
        return context

    def get_success_url(self):
        return redirect('campaigns:add_booking', self.obj.id)

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
    response['Content-Disposition'] = f'filename="{item.name}"'
    return response
