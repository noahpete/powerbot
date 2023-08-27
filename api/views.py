import os
import shutil
import time
import glob
from pathlib import Path

import django
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework import (
    viewsets,
    renderers,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from syrics.api import Spotify
from .serializers import SongSerializer, BotSerializer
from .models import Song, Songs
from .config import *
from .bot import PowerBot
from .song import Song as SongObj


def index(request):
    return render(request, 'index.html')


class SongView(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    queryset = Song.objects.all()
    most_recent_id = ""

    @action(detail=False, methods=['GET'], url_path='(?P<song_id>[^/.]+)')
    def get_track(self, request, song_id=None):
        """
        Handle GET requests to /api/songs/{song_id}/.
        """
        try:
            sp = Spotify(SP_DC)
            print('HERE: ', sp.tracks([song_id])['tracks'][0])
            song = SongObj(sp.tracks([song_id])['tracks'][0])
            return Response({
                'yt_id': song.yt_id,
                'start_time_ms': song.chorus_time_ms[0],
                'duration_ms': song.chorus_time_ms[1] - song.chorus_time_ms[0]
            })
        except Exception as e:
            return Response(
                {'message': f'Error when searching for lyrics for song with id {song_id}.',
                    'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'], url_path='lyrics/(?P<song_id>[^/.]+)')
    def get_lyrics(self, request, song_id=None):
        """
        Handle GET requests to /api/songs/lyrics/{song_id}/."""
        try:
            sp = Spotify(SP_DC)
            return Response(sp.get_lyrics(song_id))
        except Exception as e:
            return Response(
                {'message': f'Error when searching for song with id {song_id}.',
                    'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'], url_path='search/(?P<search_term>[^/.]+)')
    def search_track(self, request, max_attempts=10, search_term=None):
        """
        Handle GET requests to /api/songs/search/{search_term}/.
        """
        attempts = 0
        while attempts < max_attempts:
            try:
                sp = Spotify(SP_DC)
                results = sp.search(search_term, type='track', limit=10)
                return JsonResponse(results)
            except Exception as e:
                attempts += 1
                print(f'Retrying... Attempt {attempts}/{max_attempts}')
                time.sleep(5)  # Add a small delay before retrying
        return Response(
            {'message': 'Error in song search.', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BotView(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    queryset = Songs.objects.all()

    @action(detail=False, methods=['POST', 'GET'], url_path='generate')
    def generate(self, request):
        """
        Handle POST requests to /api/bot/generate/.
        """
        if DOWNLOAD_MODE and request.session.items():
            prev_dir = Path(f'./api/{request.session["id"]}temp')
            prev_out = Path(f'./{request.session["id"]}output.mp4')
            if prev_dir.exists():
                shutil.rmtree(prev_dir)
            if prev_out.exists():
                prev_out.unlink()

        request.session.flush()
        session_id = request.data['sessionId']
        request.session['id'] = session_id
        songs = request.data['songs']
        bot = PowerBot(songs, session_id)
        processed_songs = bot.generate()
        print('Generation complete. Songs:\n', processed_songs)
        return Response(processed_songs)

    @action(detail=False, methods=['POST'], url_path='clear')
    def clear(self, request):
        """
        Handle POST requests to /api/bot/clear/. Clear temporary files used
        for current user.
        """
        if not request.data or not DOWNLOAD_MODE:
            return HttpResponse(status=201)

        session_id = next(iter(request.data.dict().keys()))
        for filename in glob.glob(f'./{session_id}*', recursive=True):
            os.remove(filename)
            print(f'Removed file: {filename}')

        shutil.rmtree(f'./api/{session_id}temp')
        print(f'Removed directory: /api/{session_id}temp')
        return HttpResponse(status=200)
