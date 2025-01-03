import time
from npmusicdata import MusicDataStorage

class NowPlayingState:
    """
    Class to represent and manage the current state of the music player.
    """
    def __init__(self):
        self.update = False
        self.album = ""
        self.album_id = ""
        self.artist = []
        self.title = ""
        self.tracks = []
        self.track = ""
        self.duration = ""
        self.elapsed = ""
        self.npclient = ""
        self.previous_state = "startup"
        self.player_state = "stopped"
        self.state_lock = False
        self.art_url = ""
        self.debug = False
        self.last_update_time = time.time()-60 # clients
        self.last_track_elapsed = 0
        self.api_payloads = [self.get_empty_payload()]
        self.last_payload = self.get_empty_payload()
        self.epoc_start = time.time()  # Track the time the album started
        self.quality = ""

    def set_last_update_time(self):
        self.last_update_time = time.time()
    
    def get_last_update_time(self):
        return self.last_update_time

    def set_album(self, album):
        self.album = album

    def get_album(self):
        return self.album

    def set_art_url(self, art_url):
        self.art_url = art_url

    def get_art_url(self):
        return self.art_url

    def set_artist(self, artist):
        self.artist = artist
    
    def get_artist(self):
        return self.artist

    def set_album_id(self, album_id):
        self.album_id = album_id

    def get_album_id(self):
        return self.album_id

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title
    
    def set_npclient(self, npclient):
        self.npclient = npclient
    
    def get_npclient(self):
        return self.npclient

    def set_tracks(self, tracks: list):
        self.tracks = tracks

    def set_track(self, track):
        self.track = track

    def set_elapsed(self, elapsed):
        current_time = int(time.time())
        # get the time the album started
        self.epoc_start = current_time - self._time_to_seconds(elapsed)
        self.elapsed = elapsed
        return

    def get_elapsed(self):
        return self.elapsed

    def set_duration(self, duration):
        self.duration = duration

    def get_duration(self):
        return self.duration

    def set_debug(self, debug):
        self.debug = debug

    def set_last_payload(self, payload):
        self.last_payload = payload

    def get_last_payload(self):
        return self.last_payload

    def get_empty_payload(self):
        return {
            "album": "",
            "artist": "",
            "title": "",
            "duration": "",
            "elapsed": "",
            "state": "",
            "npclient": ""
        }

    def get_tracks(self):
        return self.tracks
    
    def get_track(self):
        return self.track

    def add_api_payload(self, payload):
        self.api_payloads.append(payload)

    def get_api_payload(self):
        # Get the most recent payload, remove it from the list, and return it
        try:
            payload = self.api_payloads.pop(0)
        except:
            payload = self.get_empty_payload()
        return payload

    def _time_to_seconds(self, time_str):
        """
        Convert a time string in "hh:mm:ss" or "mm:ss" format to seconds.
        
        Args:
            time_str (str): Time in the format "hh:mm:ss" or "mm:ss".
            
        Returns:
            int: The total time in seconds.
        """
        try:
            parts = list(map(int, str(time_str).split(':')))
            if len(parts) == 3:  # "hh:mm:ss" format
                hours, minutes, seconds = parts
            elif len(parts) == 2:  # "mm:ss" format
                hours, minutes, seconds = 0, *parts
            else:
                hours, minutes, seconds = 0, 0, 0
        except ValueError:
            hours, minutes, seconds = 0, 0, 0

        return hours * 3600 + minutes * 60 + seconds

    def get_epoc_elapsed(self):
        # Get the elapsed time using epoc
        try:
            total_elapsed_seconds = int(time.time() - self.get_epoc_start())
        except:
            total_elapsed_seconds = 0
        elapsed_minutes = total_elapsed_seconds // 60
        elapsed_seconds = total_elapsed_seconds % 60
        elapsed = f"{elapsed_minutes}:{elapsed_seconds:02d}"
        # if elapsed time is greater than the duration, set the elapsed time to the duration
        if total_elapsed_seconds > self._time_to_seconds(self.get_duration()):
            elapsed = self.get_duration()
            # we want to set the display to go inactive here!
        return elapsed

    def get_epoc_start(self):
        return self.epoc_start

    def set_previous_state(self, previous_state):
        self.previous_state = previous_state

    def set_player_state(self, state):
        state_updates = ["playing", "paused", "stopped", "completed", "idle", "startup"]
        if state.lower() not in state_updates:
            print(f"Invalid state: set_player_state({state})")
            return
        self.set_previous_state(self.player_state)
        self.player_state = state.lower()

    def get_player_state(self):
        return self.player_state

    def update_state(self):
        # use a lock to prevent multiple threads from updating the state at the same time
        while self.state_lock:
            time.sleep(0.1)
        self.state_lock = True
        result = self._update_state()
        self.state_lock = False
        return result

    def _update_state(self):
        # if the contents of the last api payload are different from the current state,
        # then update the state from the payload and return True, else return False
        payload = self.get_api_payload()
        if payload == self.get_empty_payload():
            return False
        elif payload != self.get_last_payload():
            if payload["state"] == "playing":
                # only update the durtion/elapsed time if the player is active or playing
                self.set_duration(payload["duration"])
                self.set_elapsed(payload["elapsed"])
            self.set_last_payload(payload)
            self.set_title(payload["title"])
            self.set_artist(payload["artist"])
            self.set_album(payload["album"])
            self.set_npclient(payload["npclient"])
            self.set_player_state(payload["state"])
            if "art_url" in payload:
                self.set_art_url(payload["art_url"])
            else:
                self.set_art_url("")
                print("no url received from wiim")
            self.set_last_update_time()
            if "quality" in payload:
                self.set_quality(payload["quality"])
            else:
                self.set_quality("")
            return True
        else:
            return False

    def get_data(self):
        data = {
            "album": self.get_album(),
            "artist": self.get_artist(),
            "title": self.get_title(),
            "duration": self.get_duration(),
            "elapsed": self.get_elapsed(),
            "state": self.get_player_state(),
            "art_url": self.get_art_url(),
            "npclient": self.npclient,
            "quality": self.get_quality()
        }
        return data

    def get_artist_multi_line(self):
        if self.artist is not None:
            if len(self.artist) > 1:
                if len(self.artist) < 5:
                    # Ensure each artist name is stripped of leading/trailing spaces
                    return "\n".join(artist.strip() for artist in self.artist)
                else:
                # Add space after commas and strip whitespace from artist names
                    return ", ".join(artist.strip() for artist in self.artist)
            else:
                return self.artist[0].strip()
        else:
            return ""

    def get_artist_str(self):
        if self.artist is not None:
            if len(self.artist) > 1:
                # Strip leading/trailing spaces and join with ', ' (comma followed by a space)
                return ", ".join(artist.strip() for artist in self.artist)
            else:
                return self.artist[0].strip()
        else:
            return ""

    def get_previous_state(self):
        return self.previous_state
    
    def set_quality(self, quality):
        self.quality = quality

    def get_quality(self):
        return self.quality
    