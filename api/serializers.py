from rest_framework import serializers
from .models import Song, Songs


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('song_id', 'title', 'artists')


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Songs
        fields = ('list_id', 'song_list')
