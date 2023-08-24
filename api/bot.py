"""
Powerbot playlist generator.
"""
import os
import boto3
from syrics.api import Spotify
from lyricsgenius import Genius
from .config import *
from pathlib import Path
from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, vfx, afx, CompositeVideoClip
from .song import Song


class PowerBot():

    def __init__(self, song_jsons: list, uuid: str, max_attempts=10, token=""):
        """
        Parse song information and initialize songs/working directory.
        """
        self.songs = []
        self.sp = Spotify(SP_DC)
        self.genius = Genius(GENIUS_TOKEN)
        self.log = []
        self.removed = []
        self.id = uuid

        if DOWNLOAD_MODE:
            self.work_dir = Path(
                f'./api/{self.id}temp').mkdir(parents=True, exist_ok=True)

        for i, json in enumerate(song_jsons):
            try:
                print(f'Trying song {json["name"]}')
                song = Song(i, json, uuid)
                if song:
                    self.songs.append(song)
            except Exception as e:
                print(
                    f'Could not add song with title {json["name"]}. Error: {e}')

    def generate(self):
        for song in self.songs:
            if not song.is_valid:
                print(
                    f'Calculated {song.title} by {song.artists[0]} to be unusable.')
                continue
            self.log.append({
                'title': song.title,
                'artist': song.artists[0],
                'yt_id': song.yt_id,
                'chorus_time_ms': song.chorus_time_ms
            })

        if not DOWNLOAD_MODE:
            return self.log

        paths = []
        for i in range(len(self.songs)):
            paths.append(f'./api/{self.id}temp/{self.id}{i}v.mp4')

        clips = []
        total_duration_s = 0
        for file in paths:
            if not os.path.exists(file):
                print('PATH DOESN"T EXIST WOMP WOMP')
                continue
            try:
                clip = VideoFileClip(file).resize(OUT_DIMENSIONS)
                img = ImageClip(BG_IMAGE, duration=clip.duration)
                comp = CompositeVideoClip(
                    [img, clip]).set_duration(clip.duration).fx(vfx.fadein, FADE_DURATION_S).fx(vfx.fadeout, FADE_DURATION_S).afx(afx.audio_fadein, FADE_DURATION_S).afx(afx.audio_fadeout, FADE_DURATION_S)
                comp = comp
                clips.append(comp)
                total_duration_s += comp.duration
            except Exception as e:
                print(
                    f'Error with {file} while generating. Error: {e}')

        if not os.path.exists(f'./api/{self.id}temp/'):
            print(f'Powerhour generation cancelled.')
            return

        if len(clips) == 0:
            print(f'No valid songs to sing to :(')
            return
        else:
            for path in paths:
                print('PATHS: ', path)

        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                final = concatenate_videoclips(
                    clips).set_duration(total_duration_s)
                final.write_videofile(f'./{self.id}output.mp4')
                for val in self.log:
                    print(
                        f'{val["title"]} by {val["artist"]}, used time {val["chorus_time"]} in video {val["yt_id"]}')
                return
            except Exception as e:
                print(f'Retrying final cut. Error: {e}')
                attempts += 1
            attempts += 1
