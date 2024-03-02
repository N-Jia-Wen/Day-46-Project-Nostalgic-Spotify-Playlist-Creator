from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
REDIRECT_URI = "http://example.com"
date = input("Which year of songs do you want to listen to? Type the date in this format (YYYY-MM-DD): ")
year = int(date.split("-")[0])
URL = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(url=URL)
content = response.text

soup = BeautifulSoup(markup=content, features="html.parser")
html_element_list = soup.select("li h3")[:100]

# This removes all the html tags as well as the extra lines due to \n and \t, leaving us with just the song names:
songs_list = [song.getText().replace("\n", "").replace("\t", "") for song in html_element_list]
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt")
)

user_id = sp.current_user()["id"]
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    public=False
)

uri_list = []
for song in songs_list:
    response = sp.search(q=f"track:{song} year:{year}", type="track", limit=1)
    try:
        uri = response["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"Sorry, the song {song} was not found in Spotify. Song was not added to Spotify playlist.")
    else:
        uri_list.append(uri)


sp.playlist_add_items(
    playlist_id=playlist["id"],
    items=uri_list
    )
