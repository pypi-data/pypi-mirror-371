class home:
    titel = "Startpage"
    exittext = "See you later!"
    currentlyplaying = "Currently playing"
    noSesion = "No playback session found. Please start a playback session first."
    lijstStartText = "What do you want to do?"
    askForInputText = "Choose an option: "
    playlist = "Playlists"
    artists = "Artists"

class artists_menu:
    header = "Artists"
    lijstStartText = "Choose the artist you want to view or play:"
    askForInputText = "Choose an artist: "

class volume_control:
    header = "Volume Control"
    lijstStartText = "Choose an option:"
    askForInputText = "Enter your choice: "
    askForVolumeText = "Enter the volume level (0-100): "
    increase = "Increase Volume"
    decrease = "Decrease Volume"
    mute = "Mute Volume"
    unmute = "Unmute Volume"
    change = 10
    setVolume = "Set Volume"

class artist_submenu:
    moreInfo = False
    header = "$name"
    view = "view"
    lijstStartText = "What do you want to do?"
    askForInputText = "Choose an option: "
    populair = "popular tracks"
    allMusic = "all music"

class playlist_menu:
    header = "Playlists"
    lijstStartText = "Which song do you want to play?"
    askForInputText = "Choose a song: "

class playlist_submenu:
    header = "Playlist options"
    lijstStartText = "What do you want to do?"
    askForInputText = "Choose an option: "
    view = "view"

class playlist_tracks:
    header = "%name"
    lijstStartText = ""
    askForInputText = "Choose an option: "

class playback_menu:
    print = "1. skip previous  2. skip next\n3. play/pause\n4. refresh\n5. change volume\n6. back "
    header = "Currently playing"
    lijstStartText = "this wil not be displayed since there is a overwrite"
    askForInputText = "Choose an option: "
    text = '$name \n[white]$artists[/white] \n[green]$volume%[/green]'
    order = [
        'text',
        'albumArt',
        'progress'
    ]
class album_tracks:
    header = "$name"
    lijstStartText = "Choose a track to play:"
    askForInputText = "Choose a track: "


class generic:
    search = 'search'
    header = "please add a header to this page from the config file"
    startText = 'Choose an option:'
    askForInputText = "Enter your choice: "
    back = 'back'
    play = 'play'
    skip_next = "skip next"
    skip_previous = "skip previous"
    pause = "pause"
    resume = "resume"
    volume = "volume"
    queue = "queue"
    refresh = "refresh"
    notPlaying = "3: play"
    playing = "3: pause"
    song = "Song"
    album = "Album"
    artist = "Artist"
    songs = "Songs"
    albums = "Albums"
    artists = "Artists"

class search_menu:
    header = 'Search'
    songs = 'Songs'
    albums = 'Albums'
    artists = 'Artists'
    playlists = 'Playlists'
    lijstStartText = 'How do you want to search?'
    askForInputText = 'Choose an option: '

class search:
    askForInputText = 'Enter your search query: '
    header = 'Search results for: $query'
    no_results = 'No results found for: $query'
    lijstStartText = 'Here is what we found: '

welkome = "Welcome to Pyspotui!"


keybinds = [
    {'combo': 'h', 'action': 'startpage'},
    {'combo': 'c', 'action': 'currently_playing'},
    {'combo': 'w', 'action': 'currently_playing'},
    {'combo': 'test', 'action': 'currently_playing'},
    {'combo': 'p', 'action': 'playlists'},
    {'combo': 'ar', 'action': 'artists'},
    {'combo': 'q', 'action': 'exit'},
    {'combo': 's', 'action': 'search'},
    {'combo': 'st', 'action': 'search_songs'},
    {'combo': 'sa', 'action': 'search_albums'},
    {'combo': 'se', 'action': 'search_artists'},
    {'combo': 'sp', 'action': 'search_playlists'},
    {'combo': '>', 'action': 'next'},
    {'combo': '<', 'action': 'previous'},
    {'combo': '.', 'action': 'next'},
    {'combo': ',', 'action': 'previous'},
    {'combo': 'd', 'action': 'next'},
    {'combo': 'a', 'action': 'previous'},
    {'combo': ' ', 'action': 'play_pause'},
]
