from urllib.parse import urlencode, urlparse, parse_qs 
import json
from spotifyAuth import authToken
import requests
from main import searchSpotify

sl_id = "734fbe21"

def getSetlist(setlist_id):
    with open("setlist_key.json", "r") as file:
        data = json.load(file)
        api_key = data["key"]

    setlist_header = {
            "Accept": "application/json",
            "x-api-key":api_key
        }


    setlist_url = f"https://api.setlist.fm/rest/1.0/setlist/{setlist_id}"

    sl_request = requests.get(setlist_url,headers=setlist_header)

    if sl_request.status_code != 200:
        print(f"Couldn't fetch the setlist with error {sl_request.status_code} \n {sl_request.text}")
        quit()
    
    return sl_request.json()

def getUserURI():
    user_url = "https://api.spotify.com/v1/me"
    auth_token = authToken()
    user_header = {
        "Authorization":f"Bearer {auth_token}"
    }
    user_request = requests.get(user_url,headers=user_header)

    if user_request.status_code != 200:
        print(f"Couldn't fetch the username with error {user_request.status_code} \n {user_request.text}")
        quit()

    user_data = user_request.json()
    user_uri = user_data["id"]
    return user_uri

def createPlaylist(name,desc):
    user_uri = getUserURI()

    c_pl_url = f"https://api.spotify.com/v1/users/{user_uri}/playlists"
    auth_token = authToken()
    c_pl_header = {
        "Authorization":f"Bearer {auth_token}",
        "Content-Type":"application/json"
    }
    c_pl_body = {
        "name": name,
        "description":desc
    }

    c_pl_request = requests.post(c_pl_url, headers=c_pl_header, json=c_pl_body)

    if c_pl_request.status_code != 201:
        print(f"Couldn't create playlist with error {c_pl_request.status_code} \n {c_pl_request.text}")
        quit()

    c_pl_data = c_pl_request.json()
    playlistId = c_pl_data["id"]

    return(playlistId, c_pl_data)

def addListToPlaylist(uri_list,pl_id):
    a_pl_url = f"https://api.spotify.com/v1/playlists/{pl_id}/tracks"

    auth_token = authToken()
    a_pl_header = {
        "Authorization":f"Bearer {auth_token}",
        "Content-Type":"application/json"
    }
    a_pl_body = {
        "uris":uri_list,
        "position":0
    }

    a_pl_request= requests.post(a_pl_url, headers=a_pl_header, json=a_pl_body)

    if a_pl_request.status_code != 201:
        print(f"Couldn't add tracks to playlist with error {a_pl_request.status_code} \n {a_pl_request.text}")
        quit()

    a_pl_data = a_pl_request.json()

    return a_pl_data


if True:
    sl_data = getSetlist(sl_id)

    artist = sl_data["artist"]["name"]
    venue = sl_data["venue"]["name"]
    #tour = sl_data["tour"]["name"]
    date = sl_data["eventDate"]

    print(f"found setlist for {artist} at {venue}")

    setlist = sl_data["sets"]["set"]
    songs_uris= []
    #songs_titles = []
    for set in setlist:
        for sng in set["song"]:
            song = {"title": sng["name"],"artists":artist}
            search_result = searchSpotify(song=song)
            if search_result[1] == 200:
                songs_uris.append("spotify:track:"+search_result[0]["tracks"]["items"][0]["id"])
                #songs_titles.append(search_result[0]["tracks"]["items"][0]["name"])


    pl_name = f"{artist} {venue}"
    pl_description = f"Setlist from {artist} at {venue} on {date}"

    pl_create = createPlaylist(pl_name,pl_description)

    add_songs = addListToPlaylist(songs_uris,pl_create[0])

print("done :p")