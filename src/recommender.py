from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    speechiness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    target_danceability: float
    target_acousticness: float
    target_instrumentalness: float
    target_speechiness: float

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def score(self, user: UserProfile, song: Song) -> float:
        points = 0.0
        if song.genre == user.favorite_genre:
            points += 2.0
        if song.mood == user.favorite_mood:
            points += 1.0
        # Energy similarity: 1.0 when perfect match, 0.0 when maximally different
        points += 1.0 - abs(song.energy - user.target_energy)
        return points

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self.score(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        parts = []
        if song.genre == user.favorite_genre:
            parts.append(f"genre match ({song.genre}) +2.0")
        if song.mood == user.favorite_mood:
            parts.append(f"mood match ({song.mood}) +1.0")
        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        parts.append(f"energy similarity +{energy_sim:.2f}")
        total = self.score(user, song)
        return f"Score {total:.2f}: " + ", ".join(parts)

def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV file and return a list of song dicts with numeric fields converted."""
    import csv

    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness",
                    "instrumentalness", "speechiness"}

    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return (score, reasons) for a song matched against user preferences."""
    score = 0.0
    reasons = []

    # Genre match: +2.0
    if song["genre"] == user_prefs.get("genre"):
        score += 2.0
        reasons.append(f"genre match ({song['genre']}) (+2.0)")

    # Mood match: +1.0
    if song["mood"] == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"mood match ({song['mood']}) (+1.0)")

    # Energy similarity: 0.0 to 1.0
    energy_sim = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    score += energy_sim
    reasons.append(f"energy similarity (+{energy_sim:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
