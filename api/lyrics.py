"""
A Lyrics object holding lyrical information for a particular song.
"""
import re
import difflib
from dataclasses import dataclass


@dataclass
class Section():
    """
    One lyrical section from Genius lyrics.
    """
    label: str
    content: str
    span: tuple
    start_time_ms: int = 0


class Lyrics():
    """
    Lyrics information.
    """

    def __init__(self, spotify_lyrics: dict, genius_lyrics: str):
        """
        Create a Lyrics object with information about the given lyrics.
        """
        self.sections = self.parse_sections(genius_lyrics)
        self.sections = self.sync_sections(
            self.sections, spotify_lyrics['lines'])

    def parse_sections(self, genius_lyrics: str) -> dict:
        """
        Parse a string of Genius lyrics into its sections.
        """
        matches = re.finditer(
            r'\[([^\]]+)\]\n(.*?)\n', genius_lyrics, re.DOTALL)
        sections = []
        for match in matches:
            label = match.groups()[0].split()[0].split(':')[
                0].lstrip('[').lower()
            content = match.groups()[1]

            # use next line as content if this line is just one word or empty
            if len(content.split()) == 1:
                if match.end() < len(genius_lyrics):
                    next_line_start = match.end()
                    next_line_end = genius_lyrics.find('\n', next_line_start)
                    if next_line_end != -1 and genius_lyrics[next_line_start:next_line_end]:
                        content = genius_lyrics[next_line_start:next_line_end]
            if content:
                sections.append(Section(label, content, match.span()))
        return sections

    def sync_sections(self, sections: list, spotify_lyrics: list) -> list:
        """
        Return section start times.
        """
        cur_time_ms = 0

        for section in sections:
            for line in spotify_lyrics:
                line_start_time_ms = int(line['startTimeMs'])
                spotify_lyr = line['words'].split('(')[0]

                # case where they're seemingly disimilar bc one contains the other
                if section.content and spotify_lyr and (section.content in spotify_lyr or spotify_lyr in section.content) and line_start_time_ms > cur_time_ms:
                    section.start_time_ms = line_start_time_ms
                    cur_time_ms = line_start_time_ms
                    break

                if are_similar(section.content, spotify_lyr) and line_start_time_ms > cur_time_ms:
                    section.start_time_ms = line_start_time_ms
                    cur_time_ms = line_start_time_ms
                    break
        print('\nSECTIONS:')
        for section in sections:
            print(section, '\n')
        return sections


def are_similar(a: str, b: str, threshold=0.65):
    """
    Return whether the two strings are similar enough according to a threshold.
    """
    if not (difflib.SequenceMatcher(None, a, b).ratio() >= threshold):
        # print(f'\nCalculated the following strings to NOT be the same:')
        # print(f'  section: {a}')
        # print(f'  spotify: {b}\n')
        pass
    else:
        # print(f'\nCalculated the following strings to be the same:')
        # print(f'  section: {a}')
        # print(f'  spotify: {b}\n')
        pass
    return difflib.SequenceMatcher(None, a, b).ratio() >= threshold
