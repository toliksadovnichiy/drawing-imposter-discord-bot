import json
import random


class WordService:
    def __init__(self, path="data/words.json"):
        with open(path, "r", encoding="utf-8") as f:
            self.words = json.load(f)

    def get_random_word(self, difficulty="easy"):
        if difficulty not in self.words:
            difficulty = "easy"

        return random.choice(self.words[difficulty])