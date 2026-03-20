#!/usr/bin/env python3
"""
Genius Lyrics Scraper
Reads a CSV file with Artist and Song columns, retrieves lyrics from Genius,
and writes them to a new Lyrics column.
"""

import pandas as pd
import lyricsgenius
import time
import traceback
import os
from dotenv import load_dotenv
import sys


def get_lyrics(artist, song_title, genius_object):
    """
    Retrieves lyrics for a given song. Handles errors and edge cases.

    Args:
        artist (str): The artist name.
        song_title (str): The song title.
        genius_object (lyricsgenius.Genius): The lyricsgenius object.

    Returns:
        str: The lyrics, or None if not found or an error occurs.
    """
    try:
        # Remove any feat. or ft. from the song title, and other brackets
        song_title_cleaned = (
            song_title.split(' (feat')[0]
            .split(' (ft.')[0]
            .split(' [feat')[0]
            .split(' [ft.')[0]
            .strip()
        )
        print(f"Searching for: '{song_title_cleaned}' by '{artist}'")

        # Ensure artist and title are not empty after cleaning/stripping
        if not artist or not song_title_cleaned:
            print(f"Skipping search due to empty artist or cleaned song title.")
            return None

        # Make the API call
        song = genius_object.search_song(song_title_cleaned, artist=artist)

        if song:
            print(f"Found lyrics for '{song_title}' by '{artist}'")
            return song.lyrics
        else:
            print(f"Lyrics not found for '{song_title}' by '{artist}'")
            return None

    except Exception as e:
        print(f"Error getting lyrics for '{song_title}' by '{artist}':")
        traceback.print_exc()
        return None


def process_csv_file(filepath, genius_token, delay_seconds=10.0):
    """
    Reads a CSV file, retrieves lyrics for each song with a delay,
    and writes the lyrics to a new column in the CSV file.

    Args:
        filepath (str): The path to the CSV file.
        genius_token (str): The Genius API token.
        delay_seconds (float): Seconds to wait between API calls.
    """
    processed_count = 0
    error_count = 0
    skipped_count = 0

    try:
        # Load the CSV file
        print(f"Attempting to load CSV file: {filepath}")
        df = pd.read_csv(filepath)
        print(f"CSV loaded successfully. Shape: {df.shape}")

        # Check for required columns (case-insensitive)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['artist', 'artists']:
                column_mapping['artist'] = col
            elif col_lower in ['song', 'title', 'song title', 'track']:
                column_mapping['song'] = col

        if 'artist' not in column_mapping or 'song' not in column_mapping:
            print(f"Error: CSV must have 'Artist' and 'Song' columns.")
            print(f"Found columns: {list(df.columns)}")
            return

        artist_col = column_mapping['artist']
        song_col = column_mapping['song']

        print(f"Using columns: Artist='{artist_col}', Song='{song_col}'")

        # Initialize the Genius object
        print("Initializing Genius API client...")
        genius = lyricsgenius.Genius(
            genius_token,
            timeout=20,
            retries=2,
            remove_section_headers=True,
            verbose=False
        )
        print("Genius client initialized.")

        # Add Lyrics column if it doesn't exist
        if 'Lyrics' not in df.columns:
            df['Lyrics'] = None
            print("Added 'Lyrics' column to dataframe.")

        # Process each row
        print(f"\nStarting to process {len(df)} songs...\n")

        for idx, row in df.iterrows():
            lyrics = None

            try:
                artist = row[artist_col]
                song_title = row[song_col]

                # Convert to string and strip whitespace, check for None/empty
                artist_str = str(artist).strip() if pd.notna(artist) else ""
                song_title_str = str(song_title).strip() if pd.notna(song_title) else ""

                if not artist_str or not song_title_str:
                    print(f"Skipping row {idx} because artist ('{artist_str}') or song title ('{song_title_str}') is missing or empty.")
                    df.at[idx, 'Lyrics'] = "Skipped: Missing data"
                    skipped_count += 1
                    print(f"Waiting for {delay_seconds} seconds before next row...")
                    time.sleep(delay_seconds)
                    continue

                print(f"\nProcessing row {idx}: '{artist_str}' - '{song_title_str}'")

                # Get Lyrics
                lyrics = get_lyrics(artist_str, song_title_str, genius)

                # Write to DataFrame
                if lyrics:
                    try:
                        # Clean lyrics slightly
                        lyrics_cleaned = lyrics.replace('EmbedShare URLCopyEmbedCopy', '').strip()

                        # Check for common "lyrics not found" patterns
                        if ("lyrics for this song have yet to be released" in lyrics_cleaned.lower() or
                            ("instrumental" in lyrics_cleaned.lower() and len(lyrics_cleaned) < 150)):
                            print(f"Found placeholder/instrumental text for '{song_title_str}'")
                            df.at[idx, 'Lyrics'] = "Lyrics Not Available"
                            processed_count += 1
                        else:
                            df.at[idx, 'Lyrics'] = lyrics_cleaned
                            processed_count += 1
                    except Exception as write_e:
                        print(f"Error writing lyrics for '{song_title_str}': {write_e}")
                        df.at[idx, 'Lyrics'] = "Error writing lyrics"
                        error_count += 1
                else:
                    print(f"No lyrics found or error occurred for row {idx}.")
                    df.at[idx, 'Lyrics'] = "Lyrics Not Found/Error"
                    error_count += 1

                # Add Delay
                print(f"Waiting for {delay_seconds} seconds before next request...")
                time.sleep(delay_seconds)

            except Exception as row_e:
                print(f"\n!!! Critical error processing row {idx} !!!")
                traceback.print_exc()
                error_count += 1
                try:
                    df.at[idx, 'Lyrics'] = "Error processing row"
                except Exception as inner_e:
                    print(f"Could not write error status for row {idx}: {inner_e}")
                print(f"Waiting for {delay_seconds} seconds after row error...")
                time.sleep(delay_seconds)

        # Save the updated CSV
        print("\nSaving CSV file...")
        df.to_csv(filepath, index=False)
        print(f"Successfully processed and saved file: {filepath}")
        print(f"Summary: Processed={processed_count}, Errors/Not Found={error_count}, Skipped={skipped_count}")

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        print("Please ensure the path is correct and the file exists.")
    except ImportError as import_e:
        print(f"Import Error: {import_e}")
        print("Please ensure you have installed the required libraries: pip install -r requirements.txt")
    except Exception as e:
        print(f"\nAn unexpected error occurred during script execution:")
        traceback.print_exc()


def main():
    """Main entry point for the scraper."""
    try:
        # Load environment variables from .env file
        load_dotenv()

        # Get the Genius API token
        genius_token = os.getenv('GENIUS_API_TOKEN')

        if not genius_token:
            print("Error: GENIUS_API_TOKEN not found in environment variables.")
            print("\nYou can either:")
            print("1. Create a .env file with: GENIUS_API_TOKEN=your_token_here")
            print("2. Set the environment variable in your shell")
            print("\nGet your token at: https://genius.com/api-clients")
            sys.exit(1)

        # Get the CSV file path from command line or prompt
        if len(sys.argv) > 1:
            csv_file_path = sys.argv[1]
        else:
            csv_file_path = input("Enter the path to your CSV file: ")

        if not csv_file_path:
            print("Error: CSV file path is required.")
            sys.exit(1)

        # Set delay (adjustable via command line argument)
        if len(sys.argv) > 2:
            try:
                api_delay = float(sys.argv[2])
            except ValueError:
                print("Warning: Invalid delay value, using default 10.0 seconds")
                api_delay = 10.0
        else:
            api_delay = 10.0

        print(f"Using API delay of {api_delay} seconds between requests")

        # Process the CSV file
        process_csv_file(csv_file_path, genius_token, delay_seconds=api_delay)

    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as main_e:
        print("\nAn error occurred in the main execution block:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
