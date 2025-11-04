from urllib.parse import urlencode, urlparse, parse_qs
import requests
import base64
import webbrowser
import json
import datetime
import os

def authToken(debug=False):

    with open("spotify_codes.json","r") as file:
        data = json.load(file)
        client_id = data["client_id"]
        redirect_uri = data["redirect_uri"]
        client_secret = data["client_secret"]

    # Prepare credentials for Basic Auth header
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    token_url = "https://accounts.spotify.com/api/token"

    if os.path.exists("access_token.json"):
        current_time = datetime.datetime.now()
        with open("access_token.json", "r") as file:
            token_data = json.load(file)
        token_expiration = datetime.datetime.fromisoformat(token_data["time"])
        difference = current_time - token_expiration
        if difference.total_seconds() < (token_data["expires_in"]-120):
            if debug:
                print("Loaded auth token from file")
            return token_data["access_token"]
        if difference.total_seconds() >= (token_data["expires_in"]-120) and "refresh_token" in token_data:
            #renew auth
            
            print("token about to expire or expired, renewing...")
            
            refresh_token = token_data["refresh_token"]
            headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            body = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                }
                
            print("\n Requesting refreshed access token...")
            response = requests.post(token_url, headers=headers, data=body)
                
            if response.status_code != 200:
                print(f"Failed to get access token: {response.text}")

            current_time = datetime.datetime.now()
                    
            token_data = response.json()
            print("Successfully authenticated with Spotify!")
            token_data["time"] = current_time.isoformat()

            with open("access_token.json", "w") as file:
                json.dump(token_data, file)

            access_token = token_data.get('access_token')

            return access_token




    print("token not found \n starting the authentication process")

    scope = "user-library-modify playlist-modify-private playlist-modify-public user-read-private"
    auth_params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
        }
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"
    print(f"Taking you to:\n{auth_url}")
    webbrowser.open(auth_url)

    response_url = input("Paste the url you got redirected to: \n")
        
    try:
        parsed_url = urlparse(response_url)
        auth_code = parse_qs(parsed_url.query)['code'][0]
    except Exception:
        print("Could not parse authorization code from the URL.")
        
    # Step 2: Exchange authorization code for an access token
        
    headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
    body = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri
        }
        
    print("\nRequesting access token...")
    response = requests.post(token_url, headers=headers, data=body)
        
    if response.status_code != 200:
        print(f"Failed to get access token: {response.text}")

    current_time = datetime.datetime.now()
            
    token_data = response.json()
    print("Successfully authenticated with Spotify!")
    token_data["time"] = current_time.isoformat()

    with open("access_token.json", "w") as file:
        json.dump(token_data, file)

    access_token = token_data.get('access_token')

    return access_token
