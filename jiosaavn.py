import requests
import endpoints
import helper
import json
from traceback import print_exc

def search_for_song(query):
    search_base_url = endpoints.search_base_url+query
    response = requests.get(search_base_url).text.encode().decode('unicode-escape')
    response = json.loads(response)
    return response['songs']['data']

def get_song(id):
    song_details_base_url = endpoints.song_details_base_url+id
    song_response = requests.get(song_details_base_url).text.encode().decode('unicode-escape')
    song_response = json.loads(song_response)
    return helper.format_song(song_response[id])

def get_playlist(listId,lyrics):
    try:
        response = requests.get(endpoints.playlist_details_base_url+listId)
        if response.status_code == 200:
            songs_json = response.text.encode().decode('unicode-escape')
            songs_json = json.loads(songs_json)
            return helper.format_playlist(songs_json,lyrics)
        return None
    except Exception:
        print_exc()
        return None