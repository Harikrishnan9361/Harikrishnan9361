from .models import Destination

def locations_processor(request):
    try:
        raw_locations = Destination.objects.values_list('location', flat=True).distinct()
        locations = set()
        for loc in raw_locations:
            if loc:
                if ',' in loc:
                    parts = [p.strip() for p in loc.split(',')]
                    for part in parts:
                        if part:
                            locations.add(part)
                else:
                    locations.add(loc.strip())
        sorted_locations = sorted(list(locations))
    except Exception:
        sorted_locations = []

    current_location = request.GET.get('location', '')
    
    return {
        'all_locations': sorted_locations,
        'current_location': current_location,
    }
