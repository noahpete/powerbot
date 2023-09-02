from rest_framework import serializers
from .models import SongModel

class SongSerializer(serializers.ModelSerializer):
    """
    Serializer for /api/songs/ paths.
    """
    class Meta:
        model = SongModel
        fields = ('spotify_id', 'youtube_id', 'title', 'artists', 'chorus_start_ms', 'chorus_duration_ms')

