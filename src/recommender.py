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
    popularity: int
    release_decade: int
    lyrical_depth: float
    emotional_intensity: float
    mood_tags: List[str]

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
            points += 1.0
        if song.mood == user.favorite_mood:
            points += 0.5
        points += 2.0 * (1.0 - abs(song.energy - user.target_energy))
        return points

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self.score(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        parts = []
        if song.genre == user.favorite_genre:
            parts.append(f"genre match ({song.genre}) +1.0")
        if song.mood == user.favorite_mood:
            parts.append(f"mood match ({song.mood}) +0.5")
        energy_sim = 2.0 * (1.0 - abs(song.energy - user.target_energy))
        parts.append(f"energy similarity +{energy_sim:.2f}")
        total = self.score(user, song)
        return f"Score {total:.2f}: " + ", ".join(parts)

# ---------------------------------------------------------------------------
# Strategy pattern: each strategy is a dict of weight multipliers that
# reshapes which signals dominate the score.  The scoring math stays the
# same — only the weights change.  To add a new strategy, add an entry here.
# ---------------------------------------------------------------------------
STRATEGIES: Dict[str, Dict[str, float]] = {
    # Current default — all 8 signals contribute proportionally.
    "balanced": {
        "genre":               1.0,   # max +1.0
        "mood":                0.5,   # max +0.5
        "energy":              2.0,   # max +2.0
        "popularity":          0.5,   # max +0.5
        "decade":              0.75,  # max +0.75
        "lyrical_depth":       0.5,   # max +0.5
        "emotional_intensity": 0.75,  # max +0.75
        "mood_tags":           1.0,   # max +1.0
    },
    # Genre-first — categorical labels dominate.  Energy and tags
    # are secondary; everything else is de-emphasized.
    "genre_first": {
        "genre":               3.0,   # max +3.0  (tripled)
        "mood":                2.0,   # max +2.0  (quadrupled)
        "energy":              1.0,   # max +1.0  (halved)
        "popularity":          0.25,  # max +0.25
        "decade":              0.25,  # max +0.25
        "lyrical_depth":       0.25,  # max +0.25
        "emotional_intensity": 0.25,  # max +0.25
        "mood_tags":           0.5,   # max +0.5
    },
    # Vibe-match — how a song FEELS matters most.  Mood tags,
    # emotional intensity, and energy drive rankings.  Genre and
    # decade are nearly irrelevant.
    "vibe_match": {
        "genre":               0.25,  # max +0.25 (de-emphasized)
        "mood":                0.5,   # max +0.5
        "energy":              2.0,   # max +2.0
        "popularity":          0.25,  # max +0.25
        "decade":              0.0,   # disabled
        "lyrical_depth":       0.5,   # max +0.5
        "emotional_intensity": 1.5,   # max +1.5  (doubled)
        "mood_tags":           2.0,   # max +2.0  (doubled)
    },
    # Discovery — designed to surface songs outside the user's comfort
    # zone.  Popularity is INVERTED (prefer underground tracks), decade
    # is disabled, and mood tags / emotional intensity drive the ranking.
    "discovery": {
        "genre":               0.0,   # disabled — ignore genre entirely
        "mood":                0.5,   # max +0.5
        "energy":              1.5,   # max +1.5
        "popularity":         -0.5,   # INVERTED — farther from target = better
        "decade":              0.0,   # disabled
        "lyrical_depth":       0.75,  # max +0.75
        "emotional_intensity": 1.0,   # max +1.0
        "mood_tags":           1.5,   # max +1.5
    },
}


def max_score_for_strategy(strategy: str) -> float:
    """Compute the theoretical maximum score for a given strategy."""
    w = STRATEGIES[strategy]
    # Each base signal has a max raw value of 1.0 before weighting,
    # except popularity which inverts in discovery mode.
    total = abs(w["genre"]) + abs(w["mood"]) + abs(w["energy"])
    total += abs(w["popularity"]) + abs(w["decade"])
    total += abs(w["lyrical_depth"]) + abs(w["emotional_intensity"])
    total += abs(w["mood_tags"])
    return total


def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV file and return a list of song dicts with numeric fields converted."""
    import csv

    int_fields = {"id", "tempo_bpm", "popularity", "release_decade"}
    float_fields = {"energy", "valence", "danceability", "acousticness",
                    "instrumentalness", "speechiness", "lyrical_depth",
                    "emotional_intensity"}

    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            row["mood_tags"] = row["mood_tags"].split("|")
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict,
               strategy: str = "balanced") -> Tuple[float, List[str]]:
    """Return (score, reasons) for a song matched against user preferences.

    The `strategy` parameter selects a weight configuration from STRATEGIES.
    All scoring math is identical across strategies — only the multipliers
    change.  This is the Strategy pattern: one algorithm, swappable weights.
    """
    w = STRATEGIES[strategy]
    score = 0.0
    reasons = []

    # --- Categorical signals ---

    # Genre match: 0 or 1 × weight
    if w["genre"] and song["genre"] == user_prefs.get("genre"):
        pts = w["genre"]
        score += pts
        reasons.append(f"genre match ({song['genre']}) (+{pts:.2f})")

    # Mood match: 0 or 1 × weight
    if w["mood"] and song["mood"] == user_prefs.get("mood"):
        pts = w["mood"]
        score += pts
        reasons.append(f"mood match ({song['mood']}) (+{pts:.2f})")

    # --- Numeric distance signals ---

    # Energy similarity: (1 - distance) × weight
    raw = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    pts = w["energy"] * raw
    score += pts
    reasons.append(f"energy similarity (+{pts:.2f})")

    # Popularity proximity: (1 - distance/100) × weight
    # In "discovery" mode the weight is negative, which means songs
    # FARTHER from the user's target score higher — surfacing tracks
    # outside their usual popularity range.
    if "popularity" in user_prefs:
        raw = 1.0 - abs(song["popularity"] - user_prefs["popularity"]) / 100
        pts = w["popularity"] * raw
        score += pts
        label = "popularity proximity" if w["popularity"] >= 0 else "popularity diversity"
        reasons.append(f"{label} ({'+' if pts >= 0 else ''}{pts:.2f})")

    # Decade match: tiered (exact=1.0, ±10yr=0.5, ±20yr=0.2, else=0) × weight
    if "release_decade" in user_prefs and w["decade"]:
        decade_gap = abs(song["release_decade"] - user_prefs["release_decade"])
        if decade_gap == 0:
            raw = 1.0
        elif decade_gap <= 10:
            raw = 0.5
        elif decade_gap <= 20:
            raw = 0.2
        else:
            raw = 0.0
        pts = w["decade"] * raw
        score += pts
        label = "match" if decade_gap == 0 else "near" if decade_gap <= 20 else "far"
        reasons.append(f"decade {label} ({song['release_decade']}s) (+{pts:.2f})")

    # Lyrical depth similarity: (1 - distance) × weight
    if "lyrical_depth" in user_prefs:
        raw = 1.0 - abs(song["lyrical_depth"] - user_prefs["lyrical_depth"])
        pts = w["lyrical_depth"] * raw
        score += pts
        reasons.append(f"lyrical depth (+{pts:.2f})")

    # Emotional intensity similarity: (1 - distance) × weight
    if "emotional_intensity" in user_prefs:
        raw = 1.0 - abs(song["emotional_intensity"] - user_prefs["emotional_intensity"])
        pts = w["emotional_intensity"] * raw
        score += pts
        reasons.append(f"emotional intensity (+{pts:.2f})")

    # Mood tag overlap: (matched / total) × weight
    if "mood_tags" in user_prefs and user_prefs["mood_tags"]:
        user_tags = set(user_prefs["mood_tags"])
        song_tags = set(song["mood_tags"])
        overlap = len(user_tags & song_tags)
        raw = overlap / len(user_tags)
        pts = w["mood_tags"] * raw
        score += pts
        if overlap > 0:
            matched = ", ".join(user_tags & song_tags)
            reasons.append(f"mood tags [{matched}] ({overlap}/{len(user_tags)}) (+{pts:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    strategy: str = "balanced",
                    diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top k with explanations.

    When diverse=True, uses greedy selection with diversity penalties so the
    top k results don't stack the same artist or genre.  Scores stay pure —
    the penalty only affects pick order, not the displayed score.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, strategy=strategy)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    if not diverse:
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:k]

    return _select_diverse(scored, k)


def _select_diverse(scored: List[Tuple[Dict, float, str]],
                    k: int) -> List[Tuple[Dict, float, str]]:
    """Greedy diversity-aware selection.

    Instead of sorting once and slicing, we pick one song at a time.
    Before each pick, we apply penalties to songs that share an artist
    or genre with songs already chosen:

      Artist penalty — each repeat halves the effective score:
        1st song by artist: ×1.0  (no penalty)
        2nd song by artist: ×0.50
        3rd song by artist: ×0.25  (and so on)

      Genre penalty — softer, because genre repetition is more acceptable:
        1st–2nd songs in genre: ×1.0  (no penalty)
        3rd song in genre:      ×0.70
        4th song in genre:      ×0.40

    The penalties multiply together.  A song by a repeat artist in an
    over-represented genre gets hit by both.

    The DISPLAYED score is the original, unpenalized score so the user
    can see the true match quality.  A "(diversity pick)" note is added
    to the explanation when a penalty changed the pick order.
    """
    selected: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    for _ in range(min(k, len(remaining))):
        best_idx = -1
        best_effective = -float("inf")

        for i, (song, base_score, _explanation) in enumerate(remaining):
            effective = base_score

            # Artist penalty: halve for each repeat
            artist = song["artist"]
            artist_n = artist_counts.get(artist, 0)
            if artist_n > 0:
                effective *= 0.5 ** artist_n

            # Genre penalty: kick in after 2 songs in the same genre
            genre = song["genre"]
            genre_n = genre_counts.get(genre, 0)
            if genre_n >= 3:
                effective *= 0.40
            elif genre_n >= 2:
                effective *= 0.70

            if effective > best_effective:
                best_effective = effective
                best_idx = i

        song, base_score, explanation = remaining.pop(best_idx)

        # Note when the penalty changed the outcome
        was_penalized = best_effective < base_score
        if was_penalized:
            explanation += f" | diversity pick (effective {best_effective:.2f})"

        selected.append((song, base_score, explanation))
        artist_counts[song["artist"]] = artist_counts.get(song["artist"], 0) + 1
        genre_counts[song["genre"]] = genre_counts.get(song["genre"], 0) + 1

    return selected
