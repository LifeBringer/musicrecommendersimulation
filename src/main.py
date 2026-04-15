"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate
from .recommender import load_songs, recommend_songs, STRATEGIES, max_score_for_strategy


def _wrap(text: str, width: int) -> str:
    """Word-wrap text to `width` columns, breaking on ', ' boundaries."""
    parts = text.split(", ")
    lines: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current}, {part}" if current else part
        if len(candidate) > width and current:
            lines.append(current)
            current = part
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def _score_bar(score: float, max_score: float, width: int = 20) -> str:
    """Render a small ASCII bar: [========----] 6.52/7.0"""
    ratio = max(0.0, min(score / max_score, 1.0))
    filled = round(ratio * width)
    empty = width - filled
    return f"[{'=' * filled}{'-' * empty}] {score:.2f}/{max_score:.1f}"


def print_profile_header(name: str, prefs: dict) -> None:
    """Print a clear profile header with key preferences."""
    tags = ", ".join(prefs.get("mood_tags", []))
    print(f"\n{'=' * 78}")
    print(f"  PROFILE: {name}")
    print(f"  Genre: {prefs['genre']}  |  Mood: {prefs['mood']}  "
          f"|  Energy: {prefs['energy']}  |  Popularity: {prefs.get('popularity', '-')}")
    print(f"  Decade: {prefs.get('release_decade', '-')}  "
          f"|  Lyrical depth: {prefs.get('lyrical_depth', '-')}  "
          f"|  Emotional intensity: {prefs.get('emotional_intensity', '-')}")
    if tags:
        print(f"  Mood tags: {tags}")
    print(f"{'=' * 78}")


def print_results(recs: list, max_score: float, mode_label: str) -> None:
    """Print recommendations as a formatted table with score bars and reasons."""
    print(f"\n  {mode_label}")
    print(f"  {'-' * 74}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        bar = _score_bar(score, max_score)
        title_line = f"{song['title']}\nby {song['artist']}"
        meta = f"{song['genre']} / {song['mood']}\n{song['release_decade']}s  pop:{song['popularity']}"
        reasons = _wrap(explanation, 40)

        rows.append([f"#{rank}", title_line, meta, bar, reasons])

    table = tabulate(
        rows,
        headers=["Rank", "Song", "Info", "Score", "Reasons"],
        tablefmt="simple_grid",
        stralign="left",
        colalign=("center", "left", "left", "left", "left"),
    )
    # Indent every line for visual nesting under the profile header
    for line in table.splitlines():
        print(f"  {line}")


def main() -> None:
    songs = load_songs("data/songs.csv")

    profiles = {
        "Chill Lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.38,
            "popularity": 40,
            "release_decade": 2020,
            "lyrical_depth": 0.10,
            "emotional_intensity": 0.25,
            "mood_tags": ["calm", "dreamy", "ambient"],
        },
        "High-Energy Pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.88,
            "popularity": 80,
            "release_decade": 2020,
            "lyrical_depth": 0.25,
            "emotional_intensity": 0.70,
            "mood_tags": ["uplifting", "bright", "carefree"],
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.93,
            "popularity": 45,
            "release_decade": 2000,
            "lyrical_depth": 0.55,
            "emotional_intensity": 0.88,
            "mood_tags": ["aggressive", "dark", "powerful"],
        },
        "Retro Vinyl Collector": {
            "genre": "jazz",
            "mood": "relaxed",
            "energy": 0.35,
            "popularity": 20,
            "release_decade": 1980,
            "lyrical_depth": 0.60,
            "emotional_intensity": 0.45,
            "mood_tags": ["warm", "intimate", "smooth"],
        },
        "Lyrical Storyteller": {
            "genre": "folk",
            "mood": "nostalgic",
            "energy": 0.40,
            "popularity": 25,
            "release_decade": 1970,
            "lyrical_depth": 0.80,
            "emotional_intensity": 0.55,
            "mood_tags": ["bittersweet", "reflective", "warm"],
        },
        "Party Starter": {
            "genre": "electronic",
            "mood": "euphoric",
            "energy": 0.92,
            "popularity": 85,
            "release_decade": 2020,
            "lyrical_depth": 0.15,
            "emotional_intensity": 0.85,
            "mood_tags": ["euphoric", "electric", "wild"],
        },
    }

    strategy = "balanced"
    max_score = max_score_for_strategy(strategy)

    for name, user_prefs in profiles.items():
        print_profile_header(name, user_prefs)

        for mode_label, diverse in [("STANDARD RANKING", False),
                                    ("DIVERSE RANKING", True)]:
            recs = recommend_songs(user_prefs, songs, k=5,
                                   strategy=strategy, diverse=diverse)
            print_results(recs, max_score, mode_label)

        print()


if __name__ == "__main__":
    main()
