"""
A Song class containing information for each song in the playlist.
"""
import time
import re
from .lyrics import Lyrics
from .video import Video
from .config import *


class Song():

    def __init__(self, song_json: dict):
        """
        Retrieve song information given its Spotify json.
        """
        self.is_valid = True
        temp_title = re.sub(r' \([^)]*\)', '', song_json['name'])
        self.title = re.sub(r'\bfeat\b.*', '', temp_title)
        self.artists = [artist['name'] for artist in song_json['artists']]
        self.duration_ms = int(song_json['duration_ms'])

        # locate chorus
        try:
            lyrics = self.get_lyrics(song_json)
            self.chorus_time_ms = self.get_chorus_time(lyrics)
        except Exception as e:
            print(f'Unable to fetch lyrics for {self.title}. Error:', e)
            self.is_valid = False
            return

        # get youtube video
        search_term = self.title + ' ' + self.artists[0] + ' music video'
        yt_video = Video(song_json, search_term)
        self.youtube_id = yt_video.youtube_id

        # get desired section of video
        chorus_time_from_end_ms = abs(
            self.duration_ms - self.chorus_time_ms[0])
        chorus_duration_ms = abs(
            self.chorus_time_ms[1] - self.chorus_time_ms[0])

        clip_start_ms = yt_video.duration_s * 1000 - chorus_time_from_end_ms
        clip_end_ms = clip_start_ms + chorus_duration_ms + CHORUS_BUFFER_MS

        while abs(clip_end_ms - clip_start_ms) < MIN_CHORUS_LENGTH_MS:
            clip_start_ms = max(0, clip_start_ms - 1000)
            if not clip_start_ms:
                clip_end_ms = min(yt_video.duration_s *
                                  1000, clip_end_ms + 1000)

        while abs(clip_end_ms - clip_start_ms) > MAX_CHORUS_LENGTH_MS:
            clip_end_ms = max(0, clip_start_ms - 500)
            clip_start_ms += 500

        clip_start_ms = max(0, clip_start_ms)
        clip_end_ms = min(yt_video.duration_s * 1000, clip_end_ms)

        if clip_start_ms > clip_end_ms or clip_start_ms < 0 or clip_end_ms / 1000 > yt_video.duration_s:
            print('\nClip start:', clip_start_ms)
            print('\nClip end:', clip_end_ms)
            raise Exception(f'Error when clipping video for {self.title}.')

        self.clip_time_ms = [clip_start_ms, clip_end_ms]

    def get_lyrics(self, song_json: dict) -> Lyrics:
        """
        Use this track's Spotify and Genius lyrics to parse the song.
        """
        attempts = 0
        spotify_lyrics, genius_lyrics = None, None
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                spotify_lyrics = SPOTIFY.get_lyrics(song_json['id'])['lyrics']
                break
            except Exception as e:
                print(f'Retrying fetch for Spotify lyrics for {self.title}.')
                time.sleep(CONNECTION_RETRY_DELAY_S)
                attempts += 1

        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                print('Title: ', self.title)
                song = GENIUS.search_song(self.title + ' ' + self.artists[0])
                genius_lyrics = song.lyrics
                break
            except Exception as e:
                print(f'Retrying fetch for Genius lyrics for {self.title}.')
                time.sleep(CONNECTION_RETRY_DELAY_S)
                attempts += 1

        if not spotify_lyrics:
            raise Exception(f'Unable to find Spotify lyrics for {self.title}.')

        if not genius_lyrics:
            raise Exception(f'Unable to find Genius lyrics for {self.title}.')

        return Lyrics(spotify_lyrics, genius_lyrics)

    def get_chorus_time(self, lyrics: Lyrics) -> list:
        """
        Get the chorus start and end times in ms.
        """
        chorus_adjust_ms = 0
        chorus_section, section_index = None, 0
        for label in SECTIONS_BY_PREFERENCE:
            for i, section in enumerate(lyrics.sections):
                if not section:
                    print(lyrics.sections)
                    self.chorus_present = False
                    break
                if section.label == label and section.start_time_ms > CHORUS_MIN_START_TIME_MS:
                    if label in ['hook', 'verse']:
                        chorus_adjust_ms += HOOK_VERSE_OFFSET_MS
                    chorus_section = section
                    section_index = i
                    print('\nChosen section: ', section)
                    break
            if chorus_section:
                break

        if not chorus_section:
            print('\nERROR: no chorus_section found. Using default times. \n')
            return DEFAULT_CHORUS_TIME

        # default is with chorus start in center
        start_ms = max(0, chorus_section.start_time_ms - 30000)
        end_ms = min(self.duration_ms, chorus_section.start_time_ms + 30000)

        # adjust start of chorus to start of its preceding section
        if section_index > 0:
            start_ms = lyrics.sections[section_index - 1].start_time_ms + 12000
        else:
            start_ms = 0

        # make sure next section isn't actually the chorus (if section was prechorus)
        if section_index < len(lyrics.sections) - 1:
            cur_section = lyrics.sections[section_index]
            next_section = lyrics.sections[section_index + 1]
            while cur_section.label != 'chorus' and next_section.label == 'chorus':
                section_index += 1
                cur_section = next_section
                next_section = lyrics.sections[section_index + 1]
            if next_section:
                print('\nnext_section:', next_section)
                end_ms = next_section.start_time_ms

        # final safety check
        start_ms = max(0, start_ms + chorus_adjust_ms)
        end_ms = min(self.duration_ms, end_ms + chorus_adjust_ms)
        if end_ms < start_ms:
            end_ms = min(self.duration_ms, start_ms + MIN_CHORUS_LENGTH_MS)
        print('Chosen times: ', [start_ms, end_ms])

        return [start_ms, end_ms]
