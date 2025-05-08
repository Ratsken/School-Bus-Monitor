import redis
from django.conf import settings

r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])

def store_bus_location(bus_id, lat, lng):
    r.geoadd('bus_locations', (lng, lat, bus_id))
    r.expire(f'bus:{bus_id}:locations', 86400)  # Keep data for 24h

def get_bus_locations():
    return r.geosearch('bus_locations', longitude=55.2708, latitude=25.2048, 
                    radius=500, unit='km')  # UAE-centered search