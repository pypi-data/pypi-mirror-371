import rich
import pyspotui.spotify_warper as spotifylib
from pyspotui.helpers import UI, clear, header, log, hotkey_action_function_matcher
import pyspotui.config as conf
import requests
import os
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

dotenv_path = find_dotenv()
if not dotenv_path:
    # If .env file does not exist, define a path and create it
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    # Create an empty .env file if it doesn't exist
    open(dotenv_path, "a").close()

load_dotenv(dotenv_path)


def startpage(firstRun=False):
    if not firstRun:
        clear()
        header(conf.home.titel)
    playing = playback.get_current_playback()
    if playing:
        options = [
            {"name": conf.home.currentlyplaying, "function": playback_menu},
            {"name": conf.home.playlist, "function": playlist_menu},
            {"name": conf.home.artists, "function": artists_menu},
            {"name": conf.generic.search, "function": search_menu},
            {
                "name": "exit",
                "function": lambda: (clear(), print(conf.home.exittext), exit(0)),
            },
        ]
        startpage_menu = UI(
            options, REALhotkeys, conf.home.lijstStartText, conf.home.askForInputText
        )
        startpage_menu.display_menu()
        startpage_menu.get_user_choice_and_run()
    else:
        rich.print(conf.home.noSesion)


def search_menu():
    clear()
    header(conf.search_menu.header)
    search_options = [
        {"name": conf.generic.back, "function": startpage},
        {
            "name": conf.search_menu.songs,
            "function": lambda: search_songs(query=input(conf.search.askForInputText)),
        },
        {
            "name": conf.search_menu.playlists,
            "function": lambda: search_playlists(
                query=input(conf.search.askForInputText)
            ),
        },
        {
            "name": conf.search_menu.artists,
            "function": lambda: search_artists(
                query=input(conf.search.askForInputText)
            ),
        },
        {
            "name": conf.search_menu.albums,
            "function": lambda: search_albums(query=input(conf.search.askForInputText)),
        },
    ]

    search_menu_ui = UI(
        search_options,
        REALhotkeys,
        conf.search_menu.lijstStartText,
        conf.search_menu.askForInputText,
    )
    search_menu_ui.display_menu()
    search_menu_ui.get_user_choice_and_run()


def search_songs(query):
    clear()
    header(conf.search.header.replace("$query", query))
    options = [
        {"name": conf.generic.back, "function": search_menu},
    ]
    results = search.search_songs(query)
    log(results)
    if results and "tracks" in results and results["tracks"]["items"]:
        for track in results["tracks"]["items"]:
            options.append(
                {
                    "name": f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}",
                    "function": lambda t=track: (
                        playback.add_to_queue(t["uri"]),
                        playback_menu(),
                    ),
                }
            )

        search_menu_ui = UI(
            options,
            REALhotkeys,
            conf.search.lijstStartText,
            conf.search.askForInputText,
        )
        search_menu_ui.display_menu()
        search_menu_ui.get_user_choice_and_run()
    else:
        rich.print(conf.search.no_results)


def search_playlists(query):
    clear()
    header(conf.search.header.replace("$query", query))
    options = [
        {"name": conf.generic.back, "function": search_menu},
    ]
    results = search.search_playlists(query)
    log(results)
    if results and "playlists" in results and results["playlists"]["items"]:
        for playlist in results["playlists"]["items"]:
            if (
                playlist and "name" in playlist and "uri" in playlist
            ):  # Check if playlist is not None and has required fields
                options.append(
                    {
                        "name": playlist["name"],
                        "function": lambda p=playlist: (
                            playlist_submenu(p["uri"], isFromSearch=True)
                        ),
                    }
                )

        search_menu_ui = UI(
            options,
            REALhotkeys,
            conf.search.lijstStartText,
            conf.search.askForInputText,
        )
        search_menu_ui.display_menu()
        search_menu_ui.get_user_choice_and_run()
    else:
        rich.print(conf.search.no_results)


def search_albums(query):
    clear()
    header(conf.search.header.replace("$query", query))
    options = [
        {"name": conf.generic.back, "function": search_menu},
    ]
    results = search.search_albums(query)
    log(results)
    if results and "albums" in results and results["albums"]["items"]:
        for album in results["albums"]["items"]:
            if (
                album and "name" in album and "uri" in album
            ):  # Check if album is not None and has required fields
                options.append(
                    {
                        "name": album["name"],
                        "function": lambda a=album: (album_submenu(a["uri"])),
                    }
                )

        search_menu_ui = UI(
            options,
            REALhotkeys,
            conf.search.lijstStartText,
            conf.search.askForInputText,
        )
        search_menu_ui.display_menu()
        search_menu_ui.get_user_choice_and_run()
    else:
        rich.print(conf.search.no_results)


def search_artists(query):
    clear()
    header(conf.search.header.replace("$query", query))
    options = [
        {"name": conf.generic.back, "function": search_menu},
    ]
    results = search.search_artists(query)
    log(results)
    if results and "artists" in results and results["artists"]["items"]:
        for artist in results["artists"]["items"]:
            if (
                artist and "name" in artist and "uri" in artist
            ):  # Check if artist is not None and has required fields
                options.append(
                    {
                        "name": artist["name"],
                        "function": lambda a=artist: (artist_submenu(a["uri"])),
                    }
                )

        search_menu_ui = UI(
            options,
            REALhotkeys,
            conf.search.lijstStartText,
            conf.search.askForInputText,
        )
        search_menu_ui.display_menu()
        search_menu_ui.get_user_choice_and_run()
    else:
        rich.print(conf.search.no_results)


def playlist_menu():
    clear()
    header(conf.playlist_menu.header)
    playlists = library.user_playlists()
    playlistAsOptions = [
        {"name": conf.generic.back, "function": startpage},
    ]
    log(playlists["items"])
    if playlists and "items" in playlists:
        for playlist in playlists["items"]:
            playlistAsOptions.append(
                {
                    "name": playlist["name"],
                    "function": lambda p=playlist: (playlist_submenu(p["uri"])),
                }
            )
    else:
        rich.print("No playlists found.")

    playlist_menu_ui = UI(
        playlistAsOptions,
        REALhotkeys,
        conf.playlist_menu.lijstStartText,
        conf.playlist_menu.askForInputText,
    )
    playlist_menu_ui.display_menu()
    playlist_menu_ui.get_user_choice_and_run()


def playlist_submenu(uri, isFromSearch=False):
    clear()
    playlist = library.get_playlist(uri)
    header(playlist["name"])
    options = [
        {
            "name": conf.generic.play,
            "function": lambda: (playback.play_playlist(uri), playback_menu()),
        },
        {
            "name": conf.playlist_submenu.view,
            "function": lambda: (
                view_playlist_tracks(uri, isFromSearch),
                playlist_menu(),
            ),
        },
    ]
    if not isFromSearch:
        options.append({"name": conf.generic.back, "function": playlist_menu})
    else:
        options.append({"name": conf.home.titel, "function": lambda: (startpage())})
    playlistUI = UI(
        options,
        REALhotkeys,
        conf.playlist_submenu.lijstStartText,
        conf.playlist_submenu.askForInputText,
    )
    playlistUI.display_menu()
    playlistUI.get_user_choice_and_run()


def view_playlist_tracks(playlist_id, isFromSearch=False):
    clear()
    playlist = library.get_playlist(playlist_id)
    header(conf.playlist_tracks.header.replace("%name", playlist["name"]))
    options = [
        {
            "name": "placeholder A",
            "function": showplaylistOption(playlist, isFromSearch),
        }
    ]
    playlistUI = UI(
        options,
        REALhotkeys,
        conf.playlist_tracks.lijstStartText,
        conf.playlist_tracks.askForInputText,
    )
    playlistUI.display_menu()
    playlistUI.get_user_choice_and_run()


def showplaylistOption(playlist, isFromSearch=False):
    clear()
    header(playlist["name"])
    rich.print(f"Owner: {playlist['owner']['display_name']}")
    rich.print(f"Description: {playlist['description']}")
    rich.print(f"Total tracks: {playlist['tracks']['total']}")
    options = [
        {
            "name": conf.generic.back,
            "function": lambda: (playlist_submenu(playlist["uri"], isFromSearch)),
        },
    ]
    for track in playlist["tracks"]["items"]:
        options.append(
            {
                "name": f"{track['track']['name']} - {', '.join(artist['name'] for artist in track['track']['artists'])}",
                "function": lambda t=track: (
                    playback.add_to_queue(t["track"]["uri"]),
                    playback_menu(),
                ),
            }
        )

    showplaylistOptionUI = UI(options, REALhotkeys)
    showplaylistOptionUI.display_menu()
    showplaylistOptionUI.get_user_choice_and_run()


def playback_menu():
    clear()
    header(conf.playback_menu.header)
    playing = playback.get_current_playback()
    # Create cache directory if it doesn't exist
    cache_dir = Path.home() / ".config" / "pyspotui" / "album_art_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Get album art URL and cache it
    if playing and playing["item"]["album"]["images"]:
        album_id = playing["item"]["album"]["id"]
        cache_file = cache_dir / f"{album_id}.jpg"

        if not cache_file.exists():
            # Download and cache the image
            images = playing["item"]["album"]["images"]
            image_url = images[0]["url"]
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                with open(cache_file, "wb") as f:
                    f.write(response.content)
            except requests.RequestException as e:
                rich.print("Failed to load album art")
        else:
            os.system("timg " + str(cache_file) if cache_file.exists() else "")

    # Display album art if available
    output = (
        conf.playback_menu.text.replace("$name", playing["item"]["name"])
        .replace(
            "$artists",
            ", ".join(artist["name"] for artist in playing["item"]["artists"]),
        )
        .replace("$album", playing["item"]["album"]["name"])
        .replace("$duration", str(playing["item"]["duration_ms"] // 1000))
        .replace("$volume", str(playback.volume()))
    )
    rich.print(output)

    # TODO_ add queue viewing and volume control
    options = [
        {
            "name": "<==",
            "function": lambda: (playback.skip_to_previous(), playback_menu()),
        },
        {"name": "==>", "function": lambda: (playback.skip_to_next(), playback_menu())},
        {
            "name": "play/pause",
            "function": lambda: (playback.play_pause(), playback_menu()),
        },
        {"name": conf.generic.refresh, "function": lambda: (playback_menu())},
        {"name": None, "function": lambda: (volume_control())},
        {"name": conf.generic.back, "function": startpage},
    ]
    playback_menu_ui = UI(options, REALhotkeys)
    rich.print(conf.playback_menu.print)
    if playing and not playing["is_playing"]:
        rich.print(conf.generic.notPlaying)  # Play icon when not playing
    elif playing:
        rich.print(conf.generic.playing)  # Pause icon when playing
    # playback_menu_ui.display_menu()
    playback_menu_ui.get_user_choice_and_run()


def volume_control():
    volume = playback.volume()
    clear()
    header(conf.volume_control.header)
    options = [
        {"name": conf.generic.back, "function": playback_menu},
        {
            "name": conf.volume_control.increase,
            "function": lambda: (
                playback.set_volume(min(volume + conf.volume_control.change, 100)),
                volume_control(),
            ),
        },
        {
            "name": conf.volume_control.decrease,
            "function": lambda: (
                playback.set_volume(min(volume - conf.volume_control.change, 100)),
                volume_control(),
            ),
        },
        {
            "name": conf.volume_control.setVolume,
            "function": lambda: (set_volume_safely(), volume_control()),
        },
    ]
    if volume == 0:
        options.append(
            {
                "name": conf.volume_control.unmute,
                "function": lambda: (playback.set_volume(100), volume_control()),
            }
        )
    else:
        options.append(
            {
                "name": conf.volume_control.mute,
                "function": lambda: (playback.set_volume(0), volume_control()),
            }
        )
    volume_ui = UI(
        options,
        REALhotkeys,
        conf.volume_control.lijstStartText,
        conf.volume_control.askForInputText,
    )
    volume_ui.display_menu()
    volume_ui.get_user_choice_and_run()


def set_volume_safely():
    try:
        new_volume = int(input(conf.volume_control.askForVolumeText))
        if 0 <= new_volume <= 100:
            playback.set_volume(new_volume)
        else:
            rich.print("Volume must be between 0 and 100.")
    except ValueError:
        rich.print("Invalid input. Please enter a number between 0 and 100.")
    except Exception as e:
        rich.print(f"An error occurred while setting the volume: {e}")


def artists_menu():
    clear()
    header(conf.artists_menu.header)
    artists = library.saved_artists()
    artistAsOptions = [
        {"name": conf.generic.back, "function": startpage},
    ]
    if artists and "artists" in artists:
        for artist in artists["artists"]["items"]:
            artistAsOptions.append(
                {
                    "name": artist["name"],
                    "function": lambda a=artist: (artist_submenu(a["uri"])),
                }
            )

    artist_menu_ui = UI(
        artistAsOptions,
        REALhotkeys,
        conf.artists_menu.lijstStartText,
        conf.artists_menu.askForInputText,
    )
    artist_menu_ui.display_menu()
    artist_menu_ui.get_user_choice_and_run()


def artist_submenu(artist_id):
    clear()
    artist = library.get_artist(artist_id)
    header(conf.artist_submenu.header.replace("$name", artist["name"]))
    options = [
        {"name": conf.generic.back, "function": artists_menu},
        {
            "name": conf.artist_submenu.populair,
            "function": lambda: (artist_best_tracks(artist_id)),
        },
        {
            "name": conf.artist_submenu.allMusic,
            "function": lambda: (view_albums_of_artist(artist_id)),
        },
        {
            "name": conf.generic.play,
            "function": lambda: (playback.play(artist_id), playback_menu()),
        },
    ]
    if conf.artist_submenu.moreInfo:
        options.append(
            {"name": "More Info", "function": lambda: (artist_best_tracks(artist_id))}
        )

    artist_submenu_ui = UI(
        options,
        REALhotkeys,
        conf.artist_submenu.lijstStartText,
        conf.artist_submenu.askForInputText,
    )
    artist_submenu_ui.display_menu()
    artist_submenu_ui.get_user_choice_and_run()


def view_albums_of_artist(artist_id):
    clear()
    artist = library.get_artist(artist_id)
    header(conf.artist_submenu.header.replace("$name", artist["name"]))
    options = [
        {"name": conf.generic.back, "function": lambda: (artist_submenu(artist_id))},
    ]
    albums = library.get_artist_albums(artist_id)
    log(albums)
    if albums and "items" in albums:
        for album in albums["items"]:
            # Add album type prefix to distinguish between albums, singles, etc.
            album_type_prefix = ""
            if album["album_type"] == "single":
                album_type_prefix = "[Single] "
            elif album["album_type"] == "compilation":
                album_type_prefix = "[Compilation] "
            elif album["album_type"] == "album":
                album_type_prefix = "[Album] "

            # Add release year for better identification
            release_year = (
                album["release_date"][:4] if album.get("release_date") else ""
            )
            year_suffix = f" ({release_year})" if release_year else ""

            display_name = f"{album_type_prefix}{album['name']}{year_suffix}"

            options.append(
                {
                    "name": display_name,
                    "function": lambda a=album: (album_submenu(a["uri"])),
                }
            )
    else:
        rich.print("No albums found for this artist.")

    view_albums_ui = UI(
        options,
        REALhotkeys,
        conf.artist_submenu.lijstStartText,
        conf.artist_submenu.askForInputText,
    )
    view_albums_ui.display_menu()
    view_albums_ui.get_user_choice_and_run()


def artist_best_tracks(artist_id):
    clear()
    artist = library.get_artist(artist_id)
    artistTT = library.get_artist_top_tracks(uri=artist_id)
    log("ARTIST START. " + str(artist))
    header(conf.artist_submenu.header.replace("$name", artist["name"]))
    if conf.artist_submenu.moreInfo:
        rich.print(f"Followers: {artist['followers']['total']}")
        rich.print(f"Genres: {', '.join(artist['genres'])}")
        rich.print(f"Popularity: {artist['popularity']}")
    options = [
        {"name": conf.generic.back, "function": lambda: artist_submenu(artist_id)},
    ]
    if artistTT and "tracks" in artistTT:
        for track in artistTT["tracks"]:
            options.append(
                {
                    "name": f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}",
                    "function": lambda t=track: (
                        playback.add_to_queue(t["uri"]),
                        playback_menu(),
                    ),
                }
            )
    else:
        rich.print("No top tracks found for this artist.")

    artist_submenu_ui = UI(
        options,
        REALhotkeys,
        conf.artist_submenu.lijstStartText,
        conf.artist_submenu.askForInputText,
    )
    artist_submenu_ui.display_menu()
    artist_submenu_ui.get_user_choice_and_run()


def view_album_tracks(album_id):
    clear()
    album = library.get_album(album_id)
    header(conf.album_tracks.header.replace("$name", album["name"]))
    options = [
        {"name": conf.generic.back, "function": lambda: (album_submenu(album_id))},
    ]
    for track in album["tracks"]["items"]:
        options.append(
            {
                "name": f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}",
                "function": lambda t=track: (
                    playback.add_to_queue(t["uri"]),
                    playback_menu(),
                ),
            }
        )

    view_album_tracks_ui = UI(
        options,
        REALhotkeys,
        conf.album_tracks.lijstStartText,
        conf.album_tracks.askForInputText,
    )
    view_album_tracks_ui.display_menu()
    view_album_tracks_ui.get_user_choice_and_run()


def album_submenu(album_id):
    clear()
    album = library.get_album(album_id)
    header(conf.album_tracks.header.replace("$name", album["name"]))
    options = [
        {"name": conf.generic.back, "function": artists_menu},
        {
            "name": conf.generic.play,
            "function": lambda: (playback.play(album_id), playback_menu()),
        },
        {
            "name": conf.playlist_submenu.view,
            "function": lambda: (view_album_tracks(album_id)),
        },
    ]
    album_submenu_ui = UI(
        options,
        REALhotkeys,
        conf.album_tracks.lijstStartText,
        conf.album_tracks.askForInputText,
    )
    album_submenu_ui.display_menu()
    album_submenu_ui.get_user_choice_and_run()


def build_runtime_objects():
    """Initialize and return runtime objects so they can be reused in tests."""
    global playback, library, search, REALhotkeys
    spotify = spotifylib.SpotifyWarper(
        os.environ.get("SPOTIPY_CLIENT_ID"),
        os.environ.get("SPOTIPY_CLIENT_SECRET"),
        os.environ.get("SPOTIPY_REDIRECT_URI"),
    )
    playback = spotify.Playback(spotify)
    library = spotify.Library(spotify)
    search = spotify.search(spotify)
    REALhotkeys = hotkey_action_function_matcher(
        conf.keybinds,
        actions=[
            {"name": "startpage", "function": lambda self: startpage()},
            {"name": "playlists", "function": lambda self: (playlist_menu())},
            {"name": "currently_playing", "function": lambda self: (playback_menu())},
            {"name": "artists", "function": lambda self: artists_menu()},
            {"name": "search", "function": lambda self: search_menu()},
            {"name": "search_songs", "function": lambda self: search_songs(query=input(conf.search.askForInputText))},
            {"name": "search_albums", "function": lambda self: search_albums(query=input(conf.search.askForInputText))},
            {"name": "search_artists", "function": lambda self: search_artists(query=input(conf.search.askForInputText))},
            {"name": "search_playlists", "function": lambda self: search_playlists(query=input(conf.search.askForInputText))},
            {"name": "exit", "function": lambda self: (clear(), print(conf.home.exittext), exit(0))},
            {"name": "next", "function": lambda self: (playback.skip_to_next(), self.get_user_choice_and_run(self.menu_options))},
            {"name": "previous", "function": lambda self: (playback.skip_to_previous(), self.get_user_choice_and_run(self.menu_options))},
            {"name": "play_pause", "function": lambda self: (playback.play_pause(), self.get_user_choice_and_run(self.menu_options))},
        ],
    )


def main():  # pragma: no cover - interactive
    clear()
    rich.print("Loading...")
    if not (
        os.environ.get("SPOTIPY_CLIENT_ID")
        and os.environ.get("SPOTIPY_CLIENT_SECRET")
        and os.environ.get("SPOTIPY_REDIRECT_URI")
    ):
        client_id = input("Enter your SPOTIPY_CLIENT_ID: ")
        client_secret = input("Enter your SPOTIPY_CLIENT_SECRET: ")
        redirect_uri = input("Enter your SPOTIPY_REDIRECT_URI: ")

        set_key(dotenv_path, "SPOTIPY_CLIENT_ID", client_id)
        set_key(dotenv_path, "SPOTIPY_CLIENT_SECRET", client_secret)
        set_key(dotenv_path, "SPOTIPY_REDIRECT_URI", redirect_uri)

        # Also update current process
        os.environ["SPOTIPY_CLIENT_ID"] = client_id
        os.environ["SPOTIPY_CLIENT_SECRET"] = client_secret
        os.environ["SPOTIPY_REDIRECT_URI"] = redirect_uri

    build_runtime_objects()
    clear()
    rich.print(conf.welkome)
    startpage(True)


if __name__ == "__main__":  # pragma: no cover
    main()
