import django
import time
from rest_framework import viewsets, decorators, status, response
from django.shortcuts import render
from syrics.api import Spotify
from .models import SongModel
from .serializers import SongSerializer
from .song import Song
from .config import *


def index(request):
    return render(request, 'index.html')


class SongView(viewsets.ModelViewSet):
    """
    Handle HTTP requests to /api/songs/.
    """
    serializer_class = SongSerializer
    queryset = SongModel.objects.all()

    @decorators.action(detail=False, methods=['GET'], url_path='search/(?P<search_term>[^/.]+)')
    def search(self, request, search_term=None):
        """
        Handle GET requests to /api/songs/search/{search_term}/.
        """
        attempts = 0
        err = None
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                hits = SPOTIFY.search(
                    search_term, type='track', limit=MAX_SEARCH_HITS)
                return django.http.JsonResponse(hits['tracks'])
            except Exception as e:
                err = e
                attempts += 1
                print(
                    f'Retrying search for [{search_term}]. Attempt {attempts}/{MAX_CONNECTION_ATTEMPTS}')
                time.sleep(CONNECTION_RETRY_DELAY_S)
        return django.http.HttpResponse(
            {'message': f'Error when searching for [{search_term}].',
             'error': str(err)},
            status=status.HTTP_404_NOT_FOUND
        )

    @decorators.action(detail=False, methods=['GET'], url_path='(?P<song_id>[^/.]+)')
    def get_track(self, request, song_id=None):
        """
        Handle GET requests to /api/songs/{song_id}/.
        """
        try:
            song_json = SPOTIFY.tracks([song_id])['tracks'][0]
            song = Song(song_json)
            if not song.is_valid:
                return django.http.HttpResponse(404)
            print(f'Used {song.youtube_id} for {song.title} by {song.artists}.')
            return django.http.JsonResponse({
                'youtube_id': song.youtube_id,
                'start_time_ms': song.clip_time_ms[0],
                'duration_ms': song.clip_time_ms[1] - song.clip_time_ms[0]
            })
        except Exception as e:
            print('\nExc:', e)
            return django.http.HttpResponse(
                {'message': f'Error when searching for lyrics for song with id {song_id}.',
                    'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
