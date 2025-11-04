from urllib.parse import urlencode, urlparse, parse_qs 
import json
from spotifyAuth import authToken
import requests
import time

print("helo")

def searchSpotify(song):
    search_params = {
            'q':"track:"+song["title"]+" artist:"+song["artists"],
            "type": "track",
            "limit": 2
        }
    
    auth_token = authToken()
    search_header = {
        "Authorization":f"Bearer {auth_token}"
    }

    search_url = f"https://api.spotify.com/v1/search?{urlencode(search_params)}"
    search_response = requests.get(search_url,headers=search_header)

    if search_response.status_code != 200:
        print(f"Failed to seach for {song["title"]} by {song["artists"]} with code {search_response.status_code}: \n {search_response.text}")
        return [0,search_response.status_code,0,0,song]
    
    search_data = search_response.json()
    #first result at search_data["tracks"]["items"][0]
    #has these keys: ['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'is_playable', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri']
    
    name_match = False 
    artist_match = False
    if search_data["tracks"]["total"]==0:
        print(f"Couldn't find {song["title"]} by {song["artists"]}")
        return [0,404,0,0,song]
    if song["title"] == search_data["tracks"]["items"][0]["name"]:
        name_match = True
    if song["artists"] == search_data["tracks"]["items"][0]["artists"][0]["name"]:
        artist_match = True

    return [search_data,200,name_match,artist_match,song]

def addToLibrary(songList):
    lib_url = "https://api.spotify.com/v1/me/tracks"
    auth_token = authToken()
    lib_headers = {
        "Authorization":f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    if len(songList)>50:
        print("list too long dumbo, i'll split it up for you :3")
        lib_data = {
            "ids": songList[0:50]
        }
        #maybe I could use recursion here? yes i can!
        #return songList[49:]
    else:
        lib_data = {
            "ids": songList
        }
    lib_response = requests.put(lib_url,headers=lib_headers,json=lib_data)
    if lib_response.status_code !=200:
        print(f"Failed to add list of songs to the library with code {lib_response.status_code}: \n {lib_response.text}")
        return songList

    if len(songList)>50:
        addToLibrary(songList[50:])
    
    return 0

def findSongs(songList):
    combined_liked_songs = []
    search_results_ids = []
    skipped_songs = []
    for song in songList:
        if song["artists"] in artist_skips:
            continue
        search_result=searchSpotify(song)

        if search_result[1] == 429:
            print("we gotta worry about the rate limit :(")
            break

        if search_result[1] != 200:
            skipped_songs.append(song)
            continue

        SFY_title = song["sfy_name"] = search_result[0]["tracks"]["items"][0]["name"]
        SFY_artists = song["sfy_artists"] = search_result[0]["tracks"]["items"][0]["artists"][0]["name"]
        SFY_id = song["sfy_id"] = search_result[0]["tracks"]["items"][0]["id"]

        if not search_result[2] or not search_result[3]:
            print(f"\n \n Mismatch Found: \nYT: {song["title"]} by {song["artists"]} \nSFY: {SFY_title} by {SFY_artists}")
            user_decision = input("Keep this song? (y,n): ")
            if user_decision == "n":
                skipped_songs.append(song)
                continue
        search_results_ids.append(SFY_id)
        
        combined_liked_songs.append(song)
        pass
    with open("combined_liked_songs.json", "w") as file:
        json.dump(combined_liked_songs,file)
    with open("skipped_songs.json", "w") as file:
        json.dump(skipped_songs,file)
    
    return search_results_ids
    
artist_skips = ["King Gizzard and The Lizzard Wizard"]

if False:
    with open("liked_songs.json","r") as file:
            songs= json.load(file)
    
    print(searchSpotify(songs[12])[0]["tracks"])
else:
    if __name__ == "__main__":
        with open("liked_songs.json","r") as file:
            songs= json.load(file)

        ids_list = findSongs(songs)

        add_to_liked = addToLibrary(ids_list)

        if add_to_liked !=0:
            with open("remaining_song_ids.json", "w") as file:
                json.dump(add_to_liked,file)
        
    