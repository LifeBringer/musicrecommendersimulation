"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    profiles = {
        "Chill Lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.38,
            "valence": 0.58,
            "danceability": 0.60,
            "acousticness": 0.80,
            "instrumentalness": 0.80,
            "speechiness": 0.03,
        },
        "High-Energy Pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.88,
            "valence": 0.82,
            "danceability": 0.85,
            "acousticness": 0.10,
            "instrumentalness": 0.10,
            "speechiness": 0.05,
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.93,
            "valence": 0.40,
            "danceability": 0.55,
            "acousticness": 0.08,
            "instrumentalness": 0.30,
            "speechiness": 0.04,
        },
        # --- Edge-case / adversarial profiles ---
        "Contradictory Vibe": {
            "genre": "classical",
            "mood": "aggressive",
            "energy": 0.95,
        },
        "Nonexistent Genre": {
            "genre": "reggaeton",
            "mood": "chill",
            "energy": 0.30,
        },
        "Middle of Everything": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.50,
        },
        "Mood-Only Listener": {
            "genre": "funk",
            "mood": "euphoric",
            "energy": 0.50,
        },
        "Energy Extremist": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.0,
        },
    }

    for name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\n" + "=" * 50)
        print(f"  Profile: {name}")
        print(f"  Genre: {user_prefs['genre']}  |  Mood: {user_prefs['mood']}  |  Energy: {user_prefs['energy']}")
        print("=" * 50)
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n  {rank}. {song['title']} by {song['artist']}")
            print(f"     Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
            print(f"     Score: {score:.2f} / 3.50")
            print(f"     Why:   {explanation}")
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
