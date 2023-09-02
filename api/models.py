from django.db import models


class SongModel(models.Model):
    """
    A Song model representing an individual track.
    """
    spotify_id = models.CharField(max_length=64, default='', unique=True)
    youtube_id = models.CharField(max_length=64, default='', unique=True)
    title = models.CharField(max_length=64, default='')
    artists = models.JSONField()
    chorus_start_ms = models.IntegerField()
    chorus_duration_ms = models.IntegerField()

    def __str__(self):
        return f'{self.title} by {self.artists[0]} with Spotify ID {self.spotify_id}.'