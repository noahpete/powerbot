from django.db import models


class Song(models.Model):
    song_id = models.CharField(max_length=32, default='', unique=True)
    title = models.CharField(max_length=64, default='')
    artists = models.JSONField()

    def __str__(self):
        return self.song_id


class Songs(models.Model):
    list_id = models.IntegerField()
    song_list = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='songs',
    )

    def __str__(self):
        return f'Song list: {self.list_id}'
