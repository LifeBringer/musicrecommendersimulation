from src.recommender import Song, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist A",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
            instrumentalness=0.10,
            speechiness=0.05,
            popularity=70,
            release_decade=2020,
            lyrical_depth=0.30,
            emotional_intensity=0.65,
            mood_tags=["uplifting", "bright", "carefree"],
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist B",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
            instrumentalness=0.80,
            speechiness=0.03,
            popularity=35,
            release_decade=2020,
            lyrical_depth=0.10,
            emotional_intensity=0.25,
            mood_tags=["calm", "dreamy", "ambient"],
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_acousticness=0.2,
        target_instrumentalness=0.10,
        target_speechiness=0.05,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # The pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_acousticness=0.2,
        target_instrumentalness=0.10,
        target_speechiness=0.05,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_genre_match_adds_points():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_acousticness=0.2,
        target_instrumentalness=0.10,
        target_speechiness=0.05,
    )
    rec = make_small_recommender()
    pop_song = rec.songs[0]   # genre="pop"
    lofi_song = rec.songs[1]  # genre="lofi"

    assert rec.score(user, pop_song) > rec.score(user, lofi_song)


def test_recommend_respects_k():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_acousticness=0.2,
        target_instrumentalness=0.10,
        target_speechiness=0.05,
    )
    rec = make_small_recommender()

    assert len(rec.recommend(user, k=1)) == 1
    assert len(rec.recommend(user, k=2)) == 2
