# from django.shortcuts import render

# # Create your views here.
# # apps/core/views.py
# from django.shortcuts import render

# def home_view(request):
#     return render(request, 'core/home.html')


from django.shortcuts import render
from darta_chalani.models import Darta, Chalani
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from darta_chalani.models import Darta, Chalani

def home_view(request):
    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    context = {
        "total_darta": Darta.objects.count(),
        "total_chalani": Chalani.objects.count(),
        "total_confidential": Darta.objects.filter(is_confidential=True).count() + Chalani.objects.filter(is_confidential=True).count(),
        "expiring_soon": Darta.objects.filter(expiry_date__range=[today, next_week]).count() +
                         Chalani.objects.filter(expiry_date__range=[today, next_week]).count(),
        "recent_darta": Darta.objects.order_by('-created_at')[:5],
        "recent_chalani": Chalani.objects.order_by('-created_at')[:5],
        "followups": list(Darta.objects.filter(followup_date__range=[today, next_week])[:5]) +
                     list(Chalani.objects.filter(followup_date__range=[today, next_week])[:5]),
    }
    return render(request, 'core/home.html', context)
