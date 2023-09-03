"""
One YouTube video object.
"""
import re
from pytube import YouTube, Channel
from youtubesearchpython import VideosSearch
from .config import *
from requests import head

class Video():
    
    def __init__(self, song_json: dict, search_term: str):
        """
        Retrieve YouTube video information given a search term.
        """
        self.song_title = song_json['name']
        self.song_json = song_json
        self.youtube_id = self.select_video(search_term)
        self.duration_s = YouTube(f'https://www.youtube.com/watch?v={self.youtube_id}').length

    def select_video(self, search_term: str) -> str:
        """
        Select the best YouTube video for the given search term.
        """
        results = VideosSearch(search_term, limit=5).result()['result']

        for result in results:
            if self.is_good(result['id']):
                return result['id']
            print(
                f'Skipped video with id {result["id"]} while searching for {self.song_title}.')

        print('No good YouTube videos found.')
        for result in results:
            if self.is_usable(result['id']):
                return result['id']
            print(
                f'Video with id {result["id"]} while searching for {self.song_title} is not usable.'
            )
        raise Exception('No usable YouTube videos found.')

    def is_good(self, youtube_id: str):
        """
        Determine whether the provided YouTube video is good for Powerbot.
        """
        video = YouTube(f'https://www.youtube.com/watch?v={youtube_id}')
        channel = Channel(video.channel_url)
        num_subs = self.get_subscriber_count(channel)

        if self.song_title not in video.title:
            return False

        for phrase in YT_PHRASES_BLACKLIST:
            if phrase in video.streams[0].title:
                print(
                    f"Video {youtube_id}'s title contains a blacklisted phrase.")
                return False

        for phrase in YT_PHRASES_WHITELIST:
            if phrase in video.streams[0].title:
                print(f'Video {youtube_id} has a desired phrase.')
                return True

        if num_subs < YT_MIN_SUBSCRIBERS and video.views < YT_VIEW_THRESHOLD:
            print(video.title)
            print(f'Video {youtube_id} not popular enough for use.')
            return False
        
        if self.is_static(youtube_id):
            return False        

        if video.views > YT_VIEW_THRESHOLD:
            return True

        # video length too different from song length
        if abs(self.song_json['duration_ms'] / 1000 - video.length) > YT_SONG_DIFF_THRESHOLD_MS:
            print(
                f"Video {youtube_id}'s length ({video.length}) is too different from its corresponding song's length ({self.duration_ms / 1000}).")
            return False

        return True

    def is_usable(self, youtube_id: str):
        """
        Determine if the given YouTube video is usable for Powerbot.
        """
        video = YouTube(f'https://www.youtube.com/watch?v={youtube_id}')

        if self.song_title not in video.title:
            return False

        if 'Music Video' or 'Official Audio' in video.title:
            return True

        return False
    
    def is_static(self, youtube_id: str):
        """
        Determine if the given YouTube video is a static image.
        """
        sizes = []
        for i in range(1, 4):
            res = head(
                f'https://i.ytimg.com/vi/{youtube_id}/{i}.jpg')
            sizes.append(res.headers['content-length'])
        for i in range(1, 3):
            if abs(int(sizes[i]) - int(sizes[i - 1])) > YT_STATIC_THRESHOLD:
                return False
            if abs(int(sizes[0]) - int(sizes[-1])) > YT_STATIC_THRESHOLD:
                return False
        if (sizes[0] == sizes[1] and sizes[1] == sizes[2] and int(sizes[0]) < 500):
            return False
        print(f'Video {youtube_id} has been calculated to be static.')
        return True

    def get_subscriber_count(self, channel: Channel) -> int:
        """
        Get the number of subscribers for a given YouTube channel.
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