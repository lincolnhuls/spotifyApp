import os
import spotipy
import requests
import urllib.parse
from spotipy.oauth2 import SpotifyOAuth
from django.http import JsonResponse, HttpResponseRedirect
from dotenv import load_dotenv

load_dotenv()

# ========== Helper Functions ==========

def get_spotify_oauth():
    """Create a SpotifyOAuth instance for login flow."""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_BACKEND_REDIRECT_URI"),  # backend redirect
        scope=os.getenv("SPOTIPY_SCOPE"),
    )

def get_spotipy_client(request):
    """Return a Spotipy client if user has a valid token stored in session."""
    access_token = request.session.get("access_token")
    if not access_token:
        return None
    return spotipy.Spotify(auth=access_token)

# ========== Basic Health Check ==========

def ping(request):
    return JsonResponse({"message": "Backend is up"})

# ========== OAuth Flow ==========

def login(request):
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    print("➡️ Redirecting user to Spotify:", auth_url)
    return HttpResponseRedirect(auth_url)



def callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing code"}, status=400)

    print("🔁 Received code:", code)

    # ======================================================
    # 🔄 Which URL do we send the user back to?
    # ======================================================
    frontend_redirect = request.GET.get("redirect_uri")

    # If NOTHING was given by Expo → use the mobile deep link
    if not frontend_redirect:
        frontend_redirect = os.getenv("SPOTIPY_REDIRECT_URI")

    print("🎯 Final frontend redirect:", frontend_redirect)

    # ======================================================
    # 🎯 Spotify token request uses backend redirect
    # ======================================================
    backend_redirect_uri = os.getenv("SPOTIPY_BACKEND_REDIRECT_URI")

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": backend_redirect_uri,
        "client_id": os.getenv("SPOTIPY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIPY_CLIENT_SECRET"),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(token_url, data=payload, headers=headers)
        print("🟢 Token response status:", response.status_code)
        print("🟢 Token response text:", response.text)
        token_info = response.json()
    except Exception as e:
        return JsonResponse({"error": f"Token exchange failed: {str(e)}"}, status=400)

    if "access_token" not in token_info:
        return JsonResponse(
            {"error": "No access token returned", "details": token_info}, status=400
        )

    # ======================================================
    # Extract tokens
    # ======================================================
    access_token = token_info["access_token"]
    refresh_token = token_info.get("refresh_token", "")
    expires_in = token_info.get("expires_in")

    # ======================================================
    # Redirect back to Expo or Installed App
    # ======================================================
    params = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }

    redirect_url = f"{frontend_redirect}?{urllib.parse.urlencode(params)}"
    print("✅ Redirecting to app:", redirect_url)

    return HttpResponseRedirect(redirect_url)

# ========== Spotify Data Endpoints ==========

def top_tracks(request):
    sp = get_spotipy_client(request)
    if sp is None:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    top_tracks = sp.current_user_top_tracks(limit=20, time_range="long_term")
    tracks = [
        {
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "image": item["album"]["images"][0]["url"],
            "preview_url": item["preview_url"],
        }
        for item in top_tracks["items"]
    ]

    return JsonResponse({"top_tracks": tracks})


def top_artists(request):
    sp = get_spotipy_client(request)
    if sp is None:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    artist_ids = []
    artists_json = []

    top_tracks = sp.current_user_top_tracks(limit=20, time_range="long_term")
    for track in top_tracks["items"]:
        artist_id = track["artists"][0]["id"]
        if artist_id not in artist_ids:
            artist_ids.append(artist_id)

    for artist_id in artist_ids:
        artist = sp.artist(artist_id)
        artists_json.append({
            "name": artist["name"],
            "genres": artist["genres"],
            "followers": artist["followers"]["total"],
            "image": artist["images"][0]["url"] if artist["images"] else None,
            "spotify_url": artist["external_urls"]["spotify"],
        })

    return JsonResponse({"top_artists": artists_json})
