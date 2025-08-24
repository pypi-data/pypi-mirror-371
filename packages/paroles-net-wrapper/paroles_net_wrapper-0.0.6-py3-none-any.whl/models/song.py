from utils import get_lyrics
import os

class Song:
    def __init__(self, idx, name, link, artist):
        self.idx = idx
        self.name = name
        self.link = link
        self.artist = artist

    def __str__(self):
        return f"{self.idx}. {self.name} - {self.artist} : {self.link}"

    def get_lyrics(self, and_save=False):
        if and_save:
            self.save_lyrics()
        return get_lyrics(self.link)

    def save_lyrics(self):
        lyrics = self.get_lyrics()
        folder = f"paroles_net/{self.artist}"

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(f"{folder}/{self.name}.txt", "w") as f:
            f.write(lyrics)