import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyWarper:
    def __init__(self, client_id, client_secret, redirect_uri, scope='user-read-playback-state,user-modify-playback-state,user-library-read,user-library-modify,playlist-read-private,playlist-modify-private,playlist-modify-public,playlist-read-collaborative,user-read-private,user-follow-read'):
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))

    def get_devices(self):
        return self.sp.devices()

    class Playback:
        def __init__(self, spotify_warper, device_id=None):
            self.sp = spotify_warper.sp
            self.device_id = device_id

        def get_current_playback(self):
            return self.sp.current_playback()

        def skip_to_next(self):
            return self.sp.next_track()

        def skip_to_previous(self):
            return self.sp.previous_track()
        
        def set_volume(self, volume):
            return self.sp.volume(volume)
        
        def volume(self):
            return self.get_current_playback()['device']['volume_percent']
        
        def queue(self):
            return self.sp.queue()
    
        def add_to_queue(self, uri):
            return self.sp.add_to_queue(uri)
        
        def play_playlist(self, playlist_id):
            return self.sp.start_playback(context_uri=playlist_id)
        
        def play_pause(self):
            return self.sp.pause_playback() if self.get_current_playback()['is_playing'] else self.sp.start_playback()
        
        def play(self, uri):
            return self.sp.start_playback(context_uri=uri)
    
    class search:
        def __init__(self, spotify_warper, device_id=None):
            self.sp = spotify_warper.sp

        def search_songs(self, query, limit=20):
            return self.sp.search(q=query, type='track', limit=limit)
        
        def search_albums(self, query, limit=20):
            return self.sp.search(q=query, type='album', limit=limit)
        
        def search_artists(self, query, limit=20):
            return self.sp.search(q=query, type='artist', limit=limit)
        
        def search_playlists(self, query, limit=20):
            return self.sp.search(q=query, type='playlist', limit=limit)

    class Library:
        def __init__(self, spotify_warper, device_id=None):
            self.sp = spotify_warper.sp

        # tracks
        def saved_tracks(self, limit=20):
            return self.sp.current_user_saved_tracks(limit=limit)
        def tracks(self, limit=20):
            return self.sp.current_user_saved_tracks(limit=limit)
        
        # albums
        def saved_albums(self, limit=20):
            return self.sp.current_user_saved_albums(limit=limit)
        def albums(self, limit=20):
            return self.sp.current_user_saved_albums(limit=limit)
        
        # artiesten
        def saved_artists(self, limit=20):
            return self.sp.current_user_followed_artists(limit=limit)
        def artists(self, limit=20):
            return self.sp.current_user_followed_artists(limit=limit)
    
        # playlists
        def saved_playlists(self, limit=20):
            return self.sp.current_user_playlists(limit=limit)
        def user_playlists(self, limit=20):
            return self.sp.current_user_playlists(limit=limit)
        
        def get_artist(self, uri):
            return self.sp.artist(uri)
        
        def get_artist_top_tracks(self, uri):
            return self.sp.artist_top_tracks(uri)

        def get_album(self, uri):
            return self.sp.album(uri)
        
        def get_album_tracks(self, uri, limit=20):
            return self.sp.album_tracks(uri, limit=limit)

        def get_playlist(self, uri):
            return self.sp.playlist(uri)

        def get_playlist_tracks(self, uri, limit=20):
            return self.sp.playlist_tracks(uri, limit=limit)
        
        def get_artist_albums(self, uri, limit=20):
            return self.sp.artist_albums(uri, limit=limit)