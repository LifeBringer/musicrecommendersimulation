# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube Music combine multiple strategies to predict what a listener will enjoy. Collaborative filtering finds users with similar listening histories and recommends what those neighbors liked. Content-based filtering analyzes the attributes of songs themselves — tempo, energy, mood — and matches them to a user's established taste profile. Production systems blend both approaches with deep learning on raw audio and natural language processing on reviews and social media. Our simulation focuses on **content-based filtering**: we define a musical "vibe" through numeric features that capture how a song feels emotionally, physically, and texturally, then score each song against a user profile using weighted distance. The closer a song's vibe is to the user's preferences, the higher it ranks.

### Song Features

Each `Song` object carries the following attributes from `data/songs.csv`:

- **`energy`** (0–1) — intensity level, from calm ambient to high-powered workout tracks
- **`valence`** (0–1) — emotional positivity, from dark and moody to bright and uplifting
- **`acousticness`** (0–1) — sonic texture, from synthetic/electronic to warm/organic
- **`danceability`** (0–1) — how much the song makes you move
- **`instrumentalness`** (0–1) — whether the track is mostly instrumental or vocal-driven (high for study music, low for sing-alongs)
- **`speechiness`** (0–1) — presence of spoken or rapped words vs. purely melodic content (high for hip-hop, low for ambient)
- **`tempo_bpm`** (56–168) — beats per minute, normalized during scoring
- **`mood`** — categorical label (happy, chill, intense, relaxed, moody, focused, romantic, empowering, melancholic, euphoric, nostalgic, aggressive)
- **`genre`** — categorical label (pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, hip-hop, classical, electronic, folk, latin, metal, funk)

### UserProfile Preferences

Each `UserProfile` stores the listener's taste as target values to match against:

- **`favorite_genre`** — preferred genre (strongest scoring signal at +2.0)
- **`favorite_mood`** — preferred mood (secondary signal at +1.0)
- **`target_energy`** — desired energy level (scored by similarity, +0.0 to +1.0)
- **`target_acousticness`** — preference for acoustic vs. electronic texture (available in data, not yet used in scoring)

### Algorithm Recipe

The recommender scores every song against the user profile by adding up points from three signals:

| Signal | Points | How it works |
|---|---|---|
| **Genre match** | +2.0 | If the song's genre equals the user's `favorite_genre`, add 2.0 points. Otherwise add 0. |
| **Mood match** | +1.0 | If the song's mood equals the user's `favorite_mood`, add 1.0 point. Otherwise add 0. |
| **Energy similarity** | +0.0 – 1.0 | `1.0 - abs(song.energy - user.target_energy)`. A perfect energy match gives 1.0; the worst possible mismatch gives 0.0. |

**Maximum possible score: 4.0** (genre + mood + perfect energy).

Genre is weighted twice as heavily as mood because genre is the strongest identity signal — a user who likes "lofi" will almost never enjoy a "metal" track regardless of other attributes, whereas a "chill" vs. "relaxed" mood mismatch is a smaller gap in listening experience.

### Scoring and Ranking

The system works in two steps:

1. **Scoring** — Loop through every song in the catalog and compute its match score using the recipe above.
2. **Ranking** — Sort all scored songs from best to worst match, then return the top _k_ results along with a human-readable explanation of why each song was recommended.

#### Sample Output

![Terminal output showing top 5 recommendations with scores and reasons](terminal_output.png)

### Potential Biases

- **Genre over-prioritization.** At +2.0, genre dominates the score. A song that matches the user's genre but has the worst possible energy fit (score 2.0) still outranks a song that matches mood with a perfect energy fit (score 2.0) — and beats any song that only matches on energy and mood but not genre (max 2.0). This means the system may ignore great songs in adjacent genres that match the user's vibe perfectly.
- **Mood under-representation.** Mood only contributes 1.0 out of a possible 4.0 (25%). Two songs in the user's favorite genre will be distinguished almost entirely by energy, with mood acting as a tiebreaker at best.
- **Energy is the only numeric signal used.** Valence, danceability, acousticness, instrumentalness, and speechiness are all present in the data but currently ignored. A high-danceability user and a low-danceability user with otherwise identical profiles will receive the same recommendations.

### Complexity

The scoring loop is **O(n)** — it touches every song exactly once. The sort that follows is **O(n log n)**, but with 18 songs that is negligible. The bottleneck in a real system with millions of songs would be this loop, which is why production systems use approximate nearest-neighbor indexes instead of brute force — but the underlying scoring logic is identical.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

