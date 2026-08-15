import math
import logging
import urllib.request
import json
import ssl
from decimal import Decimal
from asgiref.sync import sync_to_async
from django.db.models import Q
from apps.stores.models import Store, SafetyStatus

logger = logging.getLogger(__name__)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS points in km using Haversine formula."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _fetch_live_osm_stores(latitude: float, longitude: float, radius_deg: float = 0.04) -> list[dict]:
    """
    Fetch real stores around given GPS coordinates using OpenStreetMap Nominatim API.
    Returns a list of dicts with name, address, lat, lon.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    lat = float(latitude)
    lon = float(longitude)
    found = []
    seen = set()

    search_terms = ["supermarket", "grocery", "market", "bozor"]
    for q in search_terms:
        if len(found) >= 8:
            break
        url = (
            f"https://nominatim.openstreetmap.org/search?"
            f"q={q}&format=json&lat={lat}&lon={lon}&bounded=1&"
            f"viewbox={lon - radius_deg},{lat + radius_deg},{lon + radius_deg},{lat - radius_deg}&limit=6"
        )
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SESPORT_Bot/1.0 (info@sesport.uz)"}
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for item in data:
                    display = item.get('display_name', '')
                    parts = [p.strip() for p in display.split(',') if p.strip()]
                    name = parts[0] if parts else q.capitalize()
                    
                    # Clean up generic names if possible
                    if name.lower() in ["uzbekistan", "tashkent", "samarkand", "bukhara"]:
                        name = f"{q.capitalize()} ({parts[1] if len(parts) > 1 else name})"
                    
                    addr = ', '.join(parts[:3]) if len(parts) >= 2 else display[:60]
                    key = (round(float(item['lat']), 4), round(float(item['lon']), 4))
                    if key not in seen:
                        seen.add(key)
                        found.append({
                            'name': name,
                            'address': addr,
                            'latitude': float(item['lat']),
                            'longitude': float(item['lon']),
                        })
        except Exception as e:
            logger.debug(f"OSM fetch for '{q}' skipped: {e}")

    return found


@sync_to_async
def get_nearby_stores(latitude: float, longitude: float, limit: int = 6) -> tuple[list, bool]:
    """
    Find stores closest to given coordinates.
    1. Fetches local DB stores and calculates distances.
    2. If fewer than 3 close stores exist in DB, queries OpenStreetMap in real-time
       to find actual real-world stores around the user, and auto-saves them into DB.
    3. Returns sorted list of (store, distance_km) and boolean is_close.
    """
    lat = float(latitude)
    lon = float(longitude)

    # 1. Fetch DB stores
    db_stores = list(Store.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ))

    # Calculate distances for existing DB stores
    store_distances = {}
    for s in db_stores:
        try:
            d = _haversine_km(lat, lon, float(s.latitude), float(s.longitude))
            store_distances[s.id] = (d, s)
        except Exception:
            continue

    # Check if we have nearby stores within 5 km in DB
    close_db_count = sum(1 for d, s in store_distances.values() if d <= 5.0)

    # 2. If not enough close stores in DB, fetch real-world stores via OpenStreetMap
    if close_db_count < 3:
        try:
            live_osm = _fetch_live_osm_stores(lat, lon)
            for item in live_osm:
                # Find or create in DB
                s_lat = Decimal(str(round(item['latitude'], 6)))
                s_lon = Decimal(str(round(item['longitude'], 6)))
                
                # Check if already exists near this point (within ~50m)
                existing = Store.objects.filter(
                    latitude__gte=s_lat - Decimal('0.0005'),
                    latitude__lte=s_lat + Decimal('0.0005'),
                    longitude__gte=s_lon - Decimal('0.0005'),
                    longitude__lte=s_lon + Decimal('0.0005'),
                ).first()

                if not existing:
                    new_store = Store.objects.create(
                        name=item['name'][:250],
                        address=item['address'],
                        latitude=s_lat,
                        longitude=s_lon,
                        rating=Decimal('4.5'),
                        safety_status=SafetyStatus.GREEN,
                        is_active=True,
                    )
                    dist = _haversine_km(lat, lon, float(s_lat), float(s_lon))
                    store_distances[new_store.id] = (dist, new_store)
                elif existing.id not in store_distances:
                    dist = _haversine_km(lat, lon, float(existing.latitude), float(existing.longitude))
                    store_distances[existing.id] = (dist, existing)
        except Exception as e:
            logger.warning(f"Error fetching live OSM stores: {e}")

    if not store_distances:
        return [], False

    # Sort all by distance ascending
    sorted_results = sorted(store_distances.values(), key=lambda x: x[0])
    top_results = [(store, round(dist, 2)) for dist, store in sorted_results[:limit]]
    is_close = top_results[0][1] <= 10.0 if top_results else False

    return top_results, is_close


@sync_to_async
def get_all_stores_list(limit: int = 30) -> list:
    """Get all active stores as plain list (no distance calc)."""
    return list(Store.objects.filter(is_active=True).order_by('name')[:limit])


@sync_to_async
def search_stores(query: str, limit: int = 15) -> list:
    """Search stores by name or address."""
    q = query.strip()
    if not q:
        return []
    return list(
        Store.objects.filter(
            is_active=True,
        ).filter(
            Q(name__icontains=q) |
            Q(address__icontains=q)
        ).order_by('name')[:limit]
    )
