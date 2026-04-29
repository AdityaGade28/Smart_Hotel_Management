from django.conf import settings

def map_api_key(request):
    """
    Passes the MAP_API_KEY from settings to all templates.
    """
    return {
        'MAP_API_KEY': settings.MAP_API_KEY
    }
