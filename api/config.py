"""Powerbot API configuration."""
from lyricsgenius import Genius
from syrics.api import Spotify

# Keys
# SP_DC =
# GENIUS_TOKEN = 'EdMkha3K4o1v6yIrh46OUx_47KrYLVhwTxVTIyyhaek2KRoz1wCgLUIJo5QWVEEv'
SPOTIFY = Spotify('AQBBl8RuaJ8Oab7AQynbfp084WVtSFXHRnM6IndflkNY1-541hgl6edRb2gI5Nvk6kgfoCeG02qTiiCn0vroCnatcckUMGTwbT5sLzkpDcBYXjn1sn0mgcwb6hzeYIzsO5xR97hsNv9M3xfR1VnF1Q1sYiim2Rgo')
GENIUS = Genius(
    'EdMkha3K4o1v6yIrh46OUx_47KrYLVhwTxVTIyyhaek2KRoz1wCgLUIJo5QWVEEv')

# Network
MAX_CONNECTION_ATTEMPTS = 5
CONNECTION_RETRY_DELAY_S = 2

# views.py
MAX_SEARCH_HITS = 10

# song.py
SECTIONS_BY_PREFERENCE = [
    'segue',
    'pre-chorus',
    'hook',
    'chorus',
    'verse',
]
CHORUS_MIN_START_TIME_MS = 10000
CHORUS_BUFFER_MS = 12000
MIN_CHORUS_LENGTH_MS = 50000
MAX_CHORUS_LENGTH_MS = 95000
DEFAULT_CHORUS_TIME = [12000, 77000]
HOOK_VERSE_OFFSET_MS = -16000
STATIC_OKAY = True

# video.py
YT_PHRASES_WHITELIST = ['(Official Video)', '(Official Music Video)']
YT_PHRASES_BLACKLIST = ['(DANCE VIDEO)', 'Tiny Desk',
                        'Reaction', 'Unofficial', '(Dance Video)']
YT_MIN_SUBSCRIBERS = 20000
YT_VIEW_THRESHOLD = 1000000
YT_SONG_DIFF_THRESHOLD_MS = 90000
YT_STATIC_THRESHOLD = 70
