from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place

def map_view(request):
    return render(request, "places/map.html")

def places_json(request):
    places = Place.objects.filter(is_active=True)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "kind": p.kind,
            "lat": p.lat,
            "lon": p.lon,
            "city": p.city,
            "address": p.address,
            "url": p.url,
            "promotions": [
                {"title": promo.title, "valid_to": str(promo.valid_to)}
                for promo in p.promotions.filter(is_active=True)
            ],
        }
        for p in places
    ]
    return JsonResponse(data, safe=False)

def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    return render(request, "places/place_detail.html", {"place": place})
