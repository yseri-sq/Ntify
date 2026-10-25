class Track:
    def __init__(self, id, title, artist, album="", cover_url="", audio_url=""):
        self.id = id
        self.title = title
        self.artist = artist
        self.album = album
        self.cover_url = cover_url
        self.audio_url = audio_url