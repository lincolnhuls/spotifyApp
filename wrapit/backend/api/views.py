import os
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=os.getenv("SPOTIPY_SCOPE"),
    )

def get_spotipy_client(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return None
    return spotipy.Spotify(auth=access_token)

def ping(request):
    return JsonResponse({"message": "Backend is up"})

def login(request):
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print("Using redirect URI:", os.getenv("SPOTIPY_REDIRECT_URI"))
    print("Redirecting user to:", auth_url)
    return HttpResponseRedirect(auth_url)

def callback(request):
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Missing code"}, status=400)

    print("🔁 Received code:", code)

    # Exchange authorization code for access and refresh tokens
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("SPOTIPY_REDIRECT_URI"),
        "client_id": os.getenv("SPOTIPY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIPY_CLIENT_SECRET"),
    }

    try:
        response = requests.post(token_url, data=payload)
        token_info = response.json()
        print("🟢 Spotify token response:", token_info)
    except Exception as e:
        print("❌ Token exchange HTTP error:", e)
        return JsonResponse({"error": f"Token exchange failed: {str(e)}"}, status=400)

    if "access_token" not in token_info:
        return JsonResponse({"error": "No access token returned", "details": token_info}, status=400)

    # Extract token info
    access_token = token_info["access_token"]
    refresh_token = token_info.get("refresh_token", "")
    expires_in = token_info.get("expires_in")

    # Redirect back to Expo deep link with the tokens
    redirect_uri = "https://auth.expo.io/@lincolnhuls/instantwrapped"
    params = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }

    redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(params)}"
    print("✅ Redirecting to Expo:", redirect_url)
    return HttpResponseRedirect(redirect_url)






# def callback(request):
#     sp_oauth = get_spotify_oauth()
#     code = request.GET.get("code")

#     try:
#         token_info = sp_oauth.get_access_token(code, check_cache=False)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

#     request.session['access_token'] = token_info['access_token']

#     query = urllib.parse.urlencode({
#         "access_token": token_info['access_token'],
#         "refresh_token": token_info.get('refresh_token', ''),
#         "expires_in": token_info['expires_in']
#     })
#     redirect_uri = f"https://auth.expo.io/@lincolnhuls/instantwrapped?{query}"
#     return HttpResponseRedirect(redirect_uri)

def top_tracks(request):
    sp = get_spotipy_client(request)
    if sp is None:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    tracks = []
    top_tracks = sp.current_user_top_tracks(limit=20, time_range='long_term')

    for item in top_tracks['items']:
        tracks.append({
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'album': item['album']['name'],
            'image': item['album']['images'][0]['url'],
            'preview_url': item['preview_url'],
        })

    return JsonResponse({'top_tracks': tracks})

def top_artists(request):
    sp = get_spotipy_client(request)
    if sp is None:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    artist_ids = []
    artists_json = []

    top_tracks = sp.current_user_top_tracks(limit=20, time_range='long_term')
    for track in top_tracks['items']:
        artist_id = track['artists'][0]['id']
        if artist_id not in artist_ids:
            artist_ids.append(artist_id)

    for artist_id in artist_ids:
        artist = sp.artist(artist_id)
        artists_json.append({
            'name': artist['name'],
            'genres': artist['genres'],
            'followers': artist['followers']['total'],
            'image': artist['images'][0]['url'] if artist['images'] else None,
            'spotify_url': artist['external_urls']['spotify']
        })

    return JsonResponse({'top_artists': artists_json})
