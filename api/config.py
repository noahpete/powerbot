"""API configuration file."""

# functionality
DOWNLOAD_MODE = False

# keys
SP_DC = 'AQBBl8RuaJ8Oab7AQynbfp084WVtSFXHRnM6IndflkNY1-541hgl6edRb2gI5Nvk6kgfoCeG02qTiiCn0vroCnatcckUMGTwbT5sLzkpDcBYXjn1sn0mgcwb6hzeYIzsO5xR97hsNv9M3xfR1VnF1Q1sYiim2Rgo'
GENIUS_TOKEN = 'EdMkha3K4o1v6yIrh46OUx_47KrYLVhwTxVTIyyhaek2KRoz1wCgLUIJo5QWVEEv'

# general settings
MAX_CONNECTION_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_MS = 2000

# song settings
MIN_INTRO_LENGTH_MS = 15000
MIN_CHORUS_LENGTH_MS = 55000
MAX_CHORUS_LENGTH_MS = 110000
MAX_CHORUS_FIX_MS = -30000
CHORUS_LENGTH_MS = 75000
CHORUS_OFFSET_MS = -10000
CHORUS_BUFFER_MS = 10000
CHORUS_INDICATOR = '[Chorus'
CHORUS_MIN_START_TIME_MS = 3000
VALID_LABELS = [
    'segue',
    'pre-chorus',
    'chorus',
    'verse'
]

# YouTube settings
YT_PHRASES_WHITELIST = ['(Official Video)', '(Official Music Video)']
YT_PHRASES_BLACKLIST = ['(DANCE VIDEO)', 'Tiny Desk',
                        'Reaction', 'Unofficial', '(Dance Video)']
YT_TITLE_SUFFIX_BLACKLIST = [' -', ' (feat', '(with', '(Parody']
YT_VIEW_THRESHOLD = 1000000
YT_STATIC_THRESHOLD = 70
YT_SONG_DIFF_THRESHOLD_MS = 60000
YT_TIME_DIFF_FOR_OFFSET_S = 40
YT_MIN_SUBSCRIBERS = 20000


# bot settings
OUT_DIMENSIONS = (1280, 720)
BG_IMAGE = './api/black.jpg'
FADE_DURATION_S = 1.5
MAX_CLIP_WRITE_ATTEMPTS = 3
SECTIONS_BY_PREFERENCE = [
    'segue',
    'pre-chorus',
    'chorus',
]

# S3 settings
# S3_SESSION = boto3.Session(
#     aws_access_key_id='',
#     aws_secret_access_key=''
# )
