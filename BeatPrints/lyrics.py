"""
Module: lyrics.py

Provides functionality for retrieving song lyrics using the LRClib API.
"""

import re
from lrclib import LrcLibAPI

from BeatPrints.spotify import TrackMetadata
from BeatPrints.errors import (
    NoLyricsAvailable,
    InvalidFormatError,
    InvalidSelectionError,
    LineLimitExceededError,
)
from BeatPrints.consts import Instrumental

# Initialize the components
i = Instrumental()


class Lyrics:
    """
    A class for interacting with the LRClib API to fetch and manage song lyrics.
    """

    def get_manual_lyrics(self) -> str:
        """
        Prompts the user to input lyrics line by line manually.
        
        Returns:
            str: The manually entered lyrics as a single string.
        """
        print("\nNo lyrics found for this track.")
        print("Please enter the lyrics line by line.")
        print("Type 'end' on a new line when you're finished.\n")
        
        lyrics_lines = []
        line_number = 1
        
        while True:
            line = input(f"{line_number:2d}. ")
            if line.lower().strip() == 'end':
                break
            lyrics_lines.append(line)
            line_number += 1
        
        if not lyrics_lines:
            print("No lyrics entered. Using placeholder text.")
            return "No lyrics available"
        
        lyrics = "\n".join(lyrics_lines)
        
        # Display the entered lyrics with line numbers for confirmation
        print("\nYou entered the following lyrics:")
        print("-" * 40)
        for i, line in enumerate(lyrics_lines, 1):
            if line.strip():
                print(f"{i:2d}. {line}")
            else:
                print(f"{i:2d}. [empty line]")
        print("-" * 40)
        
        return lyrics

    def check_instrumental(self, metadata: TrackMetadata) -> bool:
        """
        Determines if a track is instrumental.

        Args:
            metadata (TrackMetadata): The metadata of the track.

        Returns:
            bool: True if the track is instrumental (i.e., no lyrics found), False otherwise.
        """
        api = LrcLibAPI(
            user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
        )
        results = api.search_lyrics(
            track_name=metadata.name, artist_name=metadata.artist
        )

        return results[0].instrumental

    def get_lyrics(self, metadata: TrackMetadata) -> str:
        """
        Retrieves lyrics from LRClib.net for a specified track and artist.
        If no lyrics are found, prompts the user to input lyrics manually.

        Args:
            metadata (TrackMetadata): The metadata of the track.

        Returns:
            str: The lyrics of the track in plain text if available from the API,
                 manually entered lyrics if not found online, or a placeholder 
                 message for instrumental tracks.
        """
        api = LrcLibAPI(
            user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
        )
        results = api.search_lyrics(
            track_name=metadata.name, artist_name=metadata.artist
        )

        if not results:
            # No lyrics found, prompt user for manual input
            return self.get_manual_lyrics()

        if self.check_instrumental(metadata):
            return i.DESC

        lyrics = api.get_lyrics_by_id(results[0].id).plain_lyrics

        if not lyrics:
            # No lyrics content found, prompt user for manual input
            return self.get_manual_lyrics()

        # Display numbered lines for easy selection
        lines = [line for line in lyrics.split("\n")]
        print("\nLyrics with line numbers:")
        print("-" * 40)
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"{i:2d}. {line}")
            else:
                print(f"{i:2d}. [empty line]")
        print("-" * 40)

        return lyrics

    def select_lines(self, lyrics: str, selection: str) -> str:
        """
        Extracts a specific range of lines from the given song lyrics.

        Args:
            lyrics (str): The full lyrics of the song as a single string.
            selection (str): The range of lines to extract, specified in the format "start-end" (e.g., "2-5").

        Returns:
            str: A string containing exactly 4 extracted lines, separated by newline characters.

        Raises:
            InvalidFormatError: If the selection argument is not in the correct "start-end" format.
            InvalidSelectionError: If the specified range is out of bounds or otherwise invalid.
            LineLimitExceededError: If the selected range does not include exactly 4 non-empty lines.
        """

        # Split lyrics into lines
        lines = [line for line in lyrics.split("\n")]
        line_count = len(lines)

        try:
            pattern = r"^\d+-\d+$"

            # Check if selection matches the "start-end" format
            if not re.match(pattern, selection):
                print(f"Invalid format. Please use 'start-end' format (e.g., '1-4')")
                raise InvalidFormatError

            selected = [int(num) for num in selection.split("-")]

            # Validate the selection range
            if len(selected) != 2:
                print(f"Invalid format. Please use 'start-end' format (e.g., '1-4')")
                raise InvalidFormatError
            
            if selected[0] >= selected[1]:
                print(f"Start line ({selected[0]}) must be less than end line ({selected[1]})")
                raise InvalidSelectionError
                
            if selected[0] <= 0:
                print(f"Start line must be greater than 0. Available lines: 1-{line_count}")
                raise InvalidSelectionError
                
            if selected[1] > line_count:
                print(f"End line ({selected[1]}) exceeds available lines. Available lines: 1-{line_count}")
                raise InvalidSelectionError

            # Extract the selected lines and remove empty lines
            extracted = lines[selected[0] - 1 : selected[1]]
            selected_lines = [line for line in extracted if line != ""]

            # Ensure exactly 4 lines are selected
            if len(selected_lines) != 4:
                print(f"Selected range contains {len(selected_lines)} non-empty lines, but exactly 4 are required.")
                print(f"Try selecting a different range from the available lines (1-{line_count})")
                raise LineLimitExceededError

            quatrain = "\n".join(selected_lines).strip()
            return quatrain

        except Exception as e:
            raise e
