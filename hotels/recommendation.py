from .models import Hotel


def get_recommended_hotel(queryset=None):
    """
    Returns the hotel with the highest recommendation score.
    score = (rating * 0.5) + (availability_score * 0.3) + (price_score * 0.2)
    """
    if queryset is None:
        queryset = Hotel.objects.filter(is_active=True)

    best_hotel = None
    best_score = -1

    for hotel in queryset:
        score = hotel.recommendation_score()
        if score > best_score:
            best_score = score
            best_hotel = hotel

    return best_hotel, best_score


def get_hotels_with_scores(queryset=None):
    """
    Returns list of (hotel, score) tuples sorted by score descending.
    """
    if queryset is None:
        queryset = Hotel.objects.filter(is_active=True)

    scored = [(hotel, hotel.recommendation_score()) for hotel in queryset]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
