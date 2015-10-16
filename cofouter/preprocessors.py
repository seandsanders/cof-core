from django.conf import settings


def templates(request):
    return {
        'YOUTUBE_API_KEY': settings.YOUTUBE_API_KEY
    }