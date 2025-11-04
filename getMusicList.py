import ytmusicapi
from ytmusicapi import YTMusic
import json
import os

# ------------------- SETUP INSTRUCTIONS -------------------
# 1. Follow Step 2 in the README.md file to copy your cookie from the browser.
# 2. Paste the entire cookie string you copied between the double quotes below.
# 3. Save this file and run `python get_liked_songs.py` in your terminal.
#
# EXAMPLE:
# RAW_COOKIE_PASTE_HERE = "CONSENT=...; PREF=...; VISITOR_INFO1_LIVE=...;"
# ----------------------------------------------------------
RAW_COOKIE_PASTE_HERE = """"""


def setup_authentication():
    """
    Creates the headers_auth.json file from the raw cookie string.
    This bypasses the need for the interactive 'ytmusicapi setup' command.
    """
    if not os.path.exists('headers_auth.json'):
        if not RAW_COOKIE_PASTE_HERE or RAW_COOKIE_PASTE_HERE == "":
            print("SETUP REQUIRED: Please open this script (get_liked_songs.py) and paste your cookie into the 'RAW_COOKIE_PASTE_HERE' variable.")
            return False
        try:
            print("Creating authentication file (headers_auth.json)...")
            ytmusicapi.setup(filepath='headers_auth.json', headers_raw=RAW_COOKIE_PASTE_HERE)
            print("Authentication file created successfully.")
            return True
        except Exception as e:
            print(f"An error occurred during setup: {e}")
            print("Please ensure you have copied the full, correct cookie string.")
            return False
    return True

def get_all_liked_songs():
    """
    Authenticates with YouTube Music and fetches all liked songs.
    """
    # First, run the setup to ensure we have authentication
    if not setup_authentication():
        return

    try:
        # Initialize the API using the generated authentication file
        ytmusic = YTMusic('headers_auth.json')
        print("Successfully authenticated with YouTube Music.")

    except Exception as e:
        print("Authentication failed.")
        print("Please ensure the 'headers_auth.json' file is correct.")
        print(f"Error details: {e}")
        return

    try:
        print("\nFetching your liked songs... (This may take a moment depending on the size of your library)")
        
        # Fetch the liked songs playlist
        liked_songs = ytmusic.get_liked_songs(limit=99999)
        
        if not liked_songs or 'tracks' not in liked_songs:
            print("Could not find any liked songs or the playlist is empty.")
            return

        print(f"\nFound {len(liked_songs['tracks'])} liked songs!\n")
        print("-" * 40)

        all_songs = []
        for i, track in enumerate(liked_songs['tracks']):
            title = track.get('title', 'N/A')
            artists = ", ".join([artist['name'] for artist in track.get('artists', [])])
            album = track.get('album', {}).get('name', 'N/A') if track.get('album') else 'N/A'
            duration = track.get('duration', 'N/A')
            
            song_info = {
                "number": i + 1,
                "title": title,
                "artists": artists,
                "album": album,
                "duration": duration
            }
            all_songs.append(song_info)

            print(f"{i + 1}. {title}")
            print(f"   by: {artists}")
            print(f"   Album: {album} | Duration: {duration}\n")

        # Save the list to a JSON file
        with open('liked_songs.json', 'w', encoding='utf-8') as f:
            json.dump(all_songs, f, ensure_ascii=False, indent=4)
        
        print("-" * 40)
        print("All liked songs have been printed above.")
        print("A complete list has also been saved to 'liked_songs.json'.")

    except Exception as e:
        print(f"An error occurred while fetching songs: {e}")

if __name__ == "__main__":
    get_all_liked_songs()
