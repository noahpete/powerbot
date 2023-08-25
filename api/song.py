"""
A Song class containing information for each song in the playlist.
"""
import os
import re
import requests
import boto3
from pathlib import Path
from time import sleep
from pytube import YouTube, Channel
from youtubesearchpython import VideosSearch
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from lyricsgenius import Genius
from syrics.api import Spotify
from .lyrics import Lyrics
from .config import *


def upload_video(file_name, file_path):
    """
    Upload a video to S3.
    """
    try:
        # s3_bucket = os.environ.get('S3_BUCKET')
        s3_bucket = 'powerbot-working-directory'
        s3 = boto3.client('s3')
        print('\n\n', s3_bucket, s3, '\n\n')
        presigned_post = s3.generate_presigned_post(
            Bucket=s3_bucket,
            Key=file_name,
            Fields={"acl": "public-read", "Content-Type": 'video/mp4'},
            Conditions=[
                {"acl": "public-read"},
                {"Content-Type": 'video/mp4'}
            ],
            ExpiresIn=3600
        )
        print('PRESIGNED: ', presigned_post)
        response = requests.post(
            url=f'https://{s3_bucket}.s3.amazonaws.com/{file_name}',
            data=presigned_post
        )
        print(response.text)
    except Exception as e:
        print(f'Error while uploading file {file_name}. Error: {e}')


class Song():

    def __init__(self, index: int, song_json: dict, uuid: str):
        """
        Retrieve song information given its Spotify json.
        """
        self.is_valid = True
        self.index = index
        self.sp = Spotify(SP_DC)  # TODO: change to use from settings backend
        self.genius = Genius(GENIUS_TOKEN)
        self.spotify_id = song_json['id']
        self.title = song_json['name']
        self.artists = [artist['name'] for artist in song_json['artists']]
        self.duration_ms = int(song_json['duration_ms'])
        self.chorus_time_ms = [0, 0]
        self.yt_video_duration_ms = 0
        self.yt_id = None
        self.video_path = None
        self.audio_path = None
        self.lyrics = None
        self.chorus_present = True
        self.id = uuid

        # clean up title
        for suffix in YT_TITLE_SUFFIX_BLACKLIST:
            self.title = self.title.split(suffix)[0]

        # retrieve Spotify and Genius lyrics
        try:
            spotify_lyrics = self.get_spotify_lyrics(song_json['id'])
            print('past lyrics')
            genius_lyrics = self.get_genius_lyrics()
            lyrics = Lyrics(spotify_lyrics, genius_lyrics)
        except Exception as e:
            self.is_valid = False
            print(
                f'Unable to initialize {self.title} by {self.artists[0]}. Error: {e}')
            return

        self.chorus_time_ms = self.get_chorus_timestamps(lyrics)

        if not DOWNLOAD_MODE:
            search_term = self.title + ' ' + self.artists[0] + ' music video'
            try:
                self.yt_id = self.select_yt_video(search_term)
                self.yt_video_duration_ms = YouTube(
                    f'https://www.youtube.com/watch?v={self.yt_id}').length * 1000
            except Exception as e:
                print(
                    f'Unable to fetch {self.yt_id} for {search_term} from YouTube. Error: {e}')
                self.is_valid = False
                return

            chorus_time_from_end_ms = abs(
                self.duration_ms - self.chorus_time_ms[0])
            chorus_duration_ms = abs(
                self.chorus_time_ms[1] - self.chorus_time_ms[0])

            clip_start_ms = self.yt_video_duration_ms - chorus_time_from_end_ms
            clip_end_ms = clip_start_ms + chorus_duration_ms + CHORUS_BUFFER_MS

            # lengthen clip if too short
            while abs(clip_end_ms - clip_start_ms) < MIN_CHORUS_LENGTH_MS:
                clip_start_ms = max(0, clip_start_ms - 1000)
                if not clip_start_ms:
                    clip_end_ms = min(self.duration_ms, clip_end_ms + 1000)

            # final times safety check
            self.chorus_time_ms = [max(0, clip_start_ms), min(
                self.duration_ms, clip_end_ms)]
            return

        if DOWNLOAD_MODE:
            try:
                yt_video = self.download_yt_video()
            except Exception as e:
                self.is_valid = False
                print(
                    f'Unable to initialize {self.title} by {self.artists[0]}. Error: {e}')
            self.yt_video_duration_ms = yt_video.length * 1000
            self.cut_yt_video()
            self.is_valid = self.video_path and self.audio_path

    def get_chorus_timestamps(self, lyrics) -> list:
        """
        Get the chorus start and end times.
        """
        chorus_section, section_index = None, 0
        for label in SECTIONS_BY_PREFERENCE:
            for i, section in enumerate(lyrics.sections):
                if section.label == label and section.start_time_ms > CHORUS_MIN_START_TIME_MS:
                    chorus_section = section
                    section_index = i
                    print('\nChosen section: ', section)
                    break
            if chorus_section:
                break

        if not self.chorus_present:
            return [5, 65]

        # default is with chorus start in center
        start_ms = max(0, chorus_section.start_time_ms - 30000)
        end_ms = min(self.duration_ms, chorus_section.start_time_ms + 30000)

        # adjust start of chorus to start of its preceding section
        if section_index > 0:
            start_ms = lyrics.sections[section_index - 1].start_time_ms
        else:
            start_ms = 0

        if section_index < len(lyrics.sections) - 1:
            # make sure next section isn't actually the chorus (if section was prechorus)
            cur_section = lyrics.sections[section_index]
            next_section = lyrics.sections[section_index + 1]
            while cur_section.label != 'chorus' and next_section.label == 'chorus':
                section_index += 1
                cur_section = next_section
                next_section = lyrics.sections[section_index + 1]

            end_ms = next_section.start_time_ms

        return [start_ms, end_ms]

    def song_is_usable(self):
        """
        Make sure the selected song is usable.
        """
        if CHORUS_INDICATOR not in str(self.genius_lyr):
            print(
                f'Error: unable to locate chorus in Genius lyrics for {self.title} by {self.artists[0]}.')
            return False
        return True

    def yt_is_bad(self, yt_video_id):
        """
        Determine whether the provided YouTube video is usable for PowerBot.
        """
        video = YouTube(f'https://www.youtube.com/watch?v={yt_video_id}')
        channel = Channel(video.channel_url)
        num_subs = self.get_subscriber_count(channel)

        for phrase in YT_PHRASES_BLACKLIST:
            if phrase in video.title:
                print(
                    f"Video {yt_video_id}'s title contains a blacklisted phrase.")
                return True

        if self.yt_is_static(yt_video_id):
            return True

        if self.title not in video.title:
            return True

        for phrase in YT_PHRASES_WHITELIST:
            if phrase in video.title:
                print(
                    f"Video {yt_video_id}'s title contains a desired phrase.")
                return False

        # video length too different from song length
        if abs(self.duration_ms - video.length * 1000) > YT_SONG_DIFF_THRESHOLD_MS:
            print(
                f"Video {yt_video_id}'s length ({video.length}) is too different from its corresponding song's length ({self.duration_ms / 1000}).")
            return True

        return False

    def yt_is_good(self, yt_video_id):
        """
        Determine whether the provided YouTube video is usable for PowerBot.
        """
        video = YouTube(f'https://www.youtube.com/watch?v={yt_video_id}')
        channel = Channel(video.channel_url)
        num_subs = self.get_subscriber_count(channel)

        if self.title not in video.title:
            return False

        for phrase in YT_PHRASES_BLACKLIST:
            if phrase in video.streams[0].title:
                print(
                    f"Video {yt_video_id}'s title contains a blacklisted phrase.")
                return False

        for phrase in YT_PHRASES_WHITELIST:
            if phrase in video.streams[0].title:
                print(f'Video {yt_video_id} has a desired phrase.')
                return True

        if num_subs < YT_MIN_SUBSCRIBERS and video.views < YT_VIEW_THRESHOLD:
            print(video.title)
            print(f'Video {yt_video_id} not popular enough for use.')
            return False

        if self.yt_is_static(yt_video_id):
            return False

        if video.views > YT_VIEW_THRESHOLD:
            return True

        # video length too different from song length
        if abs(self.duration_ms - video.length * 1000) > YT_SONG_DIFF_THRESHOLD_MS:
            print(
                f"Video {yt_video_id}'s length ({video.length}) is too different from its corresponding song's length ({self.duration_ms / 1000}).")
            return False

        return True

    def yt_is_static(self, yt_video_id):
        """
        Return whether the specified YouTube video is a static image or not.
        """
        sizes = []
        for i in range(1, 4):
            res = requests.head(
                f'https://i.ytimg.com/vi/{yt_video_id}/{i}.jpg')
            sizes.append(res.headers['content-length'])
        for i in range(1, 3):
            if abs(int(sizes[i]) - int(sizes[i - 1])) > YT_STATIC_THRESHOLD:
                return False
            if abs(int(sizes[0]) - int(sizes[-1])) > YT_STATIC_THRESHOLD:
                return False
        if (sizes[0] == sizes[1] and sizes[1] == sizes[2] and int(sizes[0]) < 500):
            return False
        print(f'Video {yt_video_id} has been calculated to be static.')
        return True

    def get_spotify_lyrics(self, spotify_id):
        """
        Retrieve lyrics from Spotify API or None if unable to find lyrics.
        """
        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                sp_result = self.sp.get_lyrics(spotify_id)
                if sp_result:
                    return sp_result['lyrics']
                else:
                    raise Exception(
                        f'Unable to find Spotify lyrics for song with Spotify id {spotify_id}.')
            except Exception as e:
                print(f'Retrying fetch for Spotfiy lyrics. Error: {e}')
                sleep(CONNECTION_RETRY_DELAY_MS / 1000)
            attempts += 1
        raise Exception(
            f'Unable to find Spotify lyrics for song with Spotify id {spotify_id}.')

    def get_genius_lyrics(self):
        """
        Retrieve lyrics from Genius API or None if unable to find lyrics.
        """
        attempts, lyrics = 0, None
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                song = self.genius.search_song(
                    self.title + ' ' + self.artists[0])
                if CHORUS_INDICATOR not in song.lyrics:
                    print(f'No chorus found in {self.title}.')
                    self.chorus_present = False
                return song.lyrics
            except Exception as e:
                print(f'Retrying Genius lyrics fetch, got error: {e}')
                attempts += 1
                sleep(CONNECTION_RETRY_DELAY_MS / 1000)
        raise Exception('Unable to find Genius lyrics.')

    def get_subscriber_count(self, channel) -> int:
        """
        Get the number of subscribers for a YouTube channel given its url.
        """
        pattern = r'((?:\w+\W+){0,5})\b\w*subscribers\w*\b((?:\W+\w+){0,5})'
        match = re.findall(pattern, channel.about_html)
        if match:
            try:
                match = match[0][0].split('label":"')[1]
                match = match.replace('.', '').replace(
                    ' million', '0000').replace('K ', '000')
                return int(match)
            except Exception as e:
                print(f'Unable to retrieve subscriber count. Error: {e}')
                return 0
        else:
            return 0

    def select_yt_video(self, search_term) -> str:
        """
        Select the best YouTube video for the given search term and return the id.
        """
        results = VideosSearch(search_term, limit=5).result()['result']

        for result in results:
            if self.yt_is_good(result['id']):
                return result['id']
            print(
                f'Skipped video with id {result["id"]} while searching for {self.title}.')

        print('No good YouTube videos found.')
        for result in results:
            if self.yt_is_usable(result['id']):
                return result['id']
            print(
                f'Video with id {result["id"]} while searching for {self.title} is not usable.'
            )
        raise Exception('No usable YouTube videos found.')

    def yt_is_usable(self, yt_id) -> bool:
        """
        Determine if a YouTube video is adequate given its id.
        """
        video = YouTube(f'https://www.youtube.com/watch?v={yt_id}')
        channel = Channel(video.channel_url)
        num_subs = self.get_subscriber_count(channel)

        if self.title in video.title and 'Music Video' in video.title:
            return True

        if self.title in video.title and 'Official Audio' in video.title:
            return True

        return False

    def download_yt_video(self):
        """
        Download the YouTube video corresponding to this song and return its YouTube object.
        """
        search_term = self.title + ' ' + self.artists[0] + ' music video'
        attempts = 0
        try:
            self.yt_id = self.select_yt_video(search_term)
        except:
            raise Exception(
                f'Unable to fetch {self.yt_id} for {search_term} from YouTube.')
        print(f'Proceeding with {self.yt_id} for search: {search_term}')

        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                yt = YouTube(f'https://www.youtube.com/watch?v={self.yt_id}',
                             use_oauth=True,
                             allow_oauth_cache=True)

                # shift video clip start up a bit
                if abs(yt.length - self.duration_ms / 1000) > YT_TIME_DIFF_FOR_OFFSET_S:
                    self.chorus_time_ms[0] = max(
                        0, self.chorus_time_ms[0] - 15000)
                    self.chorus_time_ms[1] -= 15000

                video = yt.streams.get_highest_resolution()
                audio = yt.streams.get_audio_only()

                if os.path.exists(f'./api/{self.id}temp/'):
                    self.video_path = video.download(
                        f'./api/{self.id}temp/', filename=f'{self.id}{self.index}.mp4')
                    self.audio_path = audio.download(
                        f'./api/{self.id}temp/', filename=f'{self.id}{self.index}.mp3')
                    print('Successful fetch from YouTube.')
                return yt
            except Exception as e:
                print(
                    f'Unable to fetch {self.yt_id} for {search_term} from YouTube. Retrying... attempt {attempts}/{MAX_CONNECTION_ATTEMPTS}')
                attempts += 1
                sleep(CONNECTION_RETRY_DELAY_MS / 1000)
        self.is_valid = False
        raise Exception(
            f'Unable to fetch {self.yt_id} for {search_term} from YouTube.')

    def cut_yt_video(self):
        """
        Cut this Song's downloaded YouTube video to just the chorus.
        """
        chorus_time_from_end_ms = abs(
            self.duration_ms - self.chorus_time_ms[0])
        chorus_duration_ms = abs(
            self.chorus_time_ms[1] - self.chorus_time_ms[0])

        clip_start_ms = self.yt_video_duration_ms - chorus_time_from_end_ms
        clip_end_ms = clip_start_ms + chorus_duration_ms + CHORUS_BUFFER_MS

        # lengthen clip if too short
        while abs(clip_end_ms - clip_start_ms) < MIN_CHORUS_LENGTH_MS:
            clip_start_ms = max(0, clip_start_ms - 1000)
            if not clip_start_ms:
                clip_end_ms = min(self.duration_ms, clip_end_ms + 1000)

        # final times safety check before cilpping
        clip_start_ms = max(0, clip_start_ms)
        clip_end_ms = min(self.duration_ms, clip_end_ms)

        if os.path.exists(f'./api/{self.id}temp/'):
            file_name = f'{self.id}{self.index}'
            file_path = f'./api/{self.id}temp/{file_name}.mp4'
            ffmpeg_extract_subclip(
                file_path,
                clip_start_ms / 1000,
                clip_end_ms / 1000,
                targetname=f'./api/{self.id}temp/{self.id}{self.index}v.mp4')

            upload_video(file_name, file_path)

            print(f'Successful cut for {self.title}.')

        Path(f'./api/{self.id}temp/{self.id}{self.index}.mp4').unlink()
        Path(f'./api/{self.id}temp/{self.id}{self.index}.mp3').unlink()

        print(f'Successfully cleared temporary files for {self.title}.')
