# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

VibeFinder suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It assumes each user has a single, fixed taste profile and that musical "vibe" can be approximated by comparing numeric features. This system is built for classroom exploration and learning about how recommender systems work. It is not intended for real users, production deployment, or any setting where recommendations influence what people actually listen to.

---

## 3. How the Model Works  

Imagine you are picking songs for a friend. You know they like lofi music, they want something chill, and they prefer low-energy background tracks. You would go through your music library, check each song, and mentally score it: "This one matches their genre, that's good. The mood is right too. And the energy level is close to what they want." Then you would sort your mental list and hand them the top picks.

VibeFinder does exactly that, with numbers. For each song it checks three things:

1. Does the song's genre match what the user asked for? If yes, add 1.0 point.
2. Does the song's mood match? If yes, add 0.5 points.
3. How close is the song's energy level to the user's target? The closer it is, the more points it earns, up to a maximum of 2.0.

The maximum possible score is 3.5. Songs are sorted from highest to lowest score, and the top 5 are returned as recommendations, each with a short explanation of why it was picked.

We started with the original weights of genre +2.0, mood +1.0, and energy +1.0, but experiments showed genre was too dominant. A quiet piano piece would outrank a high-energy track just because it matched the genre label. We rebalanced to genre +1.0, mood +0.5, and energy +2.0 so that how a song actually feels matters more than what category it belongs to.

---

## 4. Data  

The catalog contains 18 songs in `data/songs.csv`. The original starter file had 10 songs; we added 8 more to improve genre and mood diversity.

Each song has 9 features: genre, mood, energy, valence, danceability, acousticness, instrumentalness, speechiness, and tempo_bpm. Of these, only genre, mood, and energy are currently used in scoring.

The catalog covers 13 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, hip-hop, classical, electronic, folk, latin, metal, funk) and 12 moods (happy, chill, intense, relaxed, moody, focused, romantic, empowering, melancholic, euphoric, nostalgic, aggressive). However, the distribution is uneven: lofi has 3 songs while most genres have only 1. Genres like country, reggae, and K-pop are absent entirely. The dataset reflects a narrow slice of English-language listening habits and does not represent global musical diversity.

---

## 5. Strengths  

The system works best for users whose taste aligns with a well-represented genre. The Chill Lofi profile gets three strong matches (Library Rain, Midnight Coding, Focus Flow) that all feel like they belong on the same study playlist. The High-Energy Pop profile correctly surfaces Sunrise City as #1 over Gym Hero because mood (happy vs. intense) breaks the tie.

The scoring logic is fully transparent. Every recommendation comes with a plain-English explanation ("genre match +1.0, mood match +0.5, energy similarity +1.94"), so a user can always understand why a song was picked. There is no black box.

The system also degrades gracefully for edge cases. When a user asks for a genre that does not exist (reggaeton), it does not crash or return nothing — it falls back on mood and energy and still returns reasonable chill tracks. When a user sets energy to 0.0 (below any song in the catalog), it still picks the lowest-energy songs available and honestly reports lower confidence scores.

---

## 6. Limitations and Bias 

The system over-relies on energy as the dominant numeric signal, which creates a filter bubble for mid-energy songs: tracks in the 0.35–0.55 energy range appear in nearly every profile's top 5 because they are never far from any user's target, while extreme-energy tracks like Frozen Lake (0.20) or Shatter Point (0.97) are systematically penalized unless a user specifically targets that extreme. Genre representation in the catalog is also uneven — lofi has three songs to differentiate between, but most genres (rock, metal, folk, classical) have exactly one, so users who prefer those genres hit a ceiling after a single strong match and the rest of their recommendations are filled by energy-proximity alone with no genre or mood relevance. Five of the eight numeric features in the dataset (valence, danceability, acousticness, instrumentalness, speechiness) are never used in scoring, meaning the system treats a bright, danceable pop track identically to a dark, slow pop ballad as long as their energy levels match. Finally, removing mood in our experiment showed that the system collapses into a pure energy-distance ranker for any user whose genre has only one song in the catalog, effectively ignoring the emotional character of music entirely for underrepresented tastes.  

---

## 7. Evaluation  

We tested eight user profiles that range from straightforward to deliberately adversarial:

- **Chill Lofi** — a study-session listener who wants low energy, acoustic, instrumental tracks
- **High-Energy Pop** — an upbeat listener who wants bright, danceable, produced music
- **Deep Intense Rock** — a headphones-on listener who wants loud, dark, aggressive tracks
- **Contradictory Vibe** — a stress test: classical genre but aggressive mood and very high energy, a combination that does not exist in the catalog
- **Nonexistent Genre** — reggaeton, which has zero songs in the catalog, forcing the system to rely entirely on mood and energy
- **Middle of Everything** — moderate energy pop/happy, designed to sit in the center of the feature space where many songs are roughly equidistant
- **Mood-Only Listener** — funk/euphoric, where only one song matches both genre and mood
- **Energy Extremist** — lofi/chill but with energy set to 0.0, well below any song in the catalog

**What we looked for:** Each profile should produce a different #1 song. Songs that match on genre, mood, and energy should rank highest. Profiles with conflicting preferences should expose which signal the system trusts most.

**What surprised us:** The biggest surprise was how genre dominated everything under the original weights (genre +2.0, mood +1.0, energy +0.0–1.0). The Contradictory Vibe profile asked for high-energy aggressive music, but the system recommended Frozen Lake — a quiet, melancholic piano piece — simply because it was the only classical song. A genre label alone outweighed a near-perfect energy match combined with a mood match. That felt wrong in the way a real bad recommendation feels wrong: technically explainable, but clearly not what the listener wanted.

The second surprise was "Gym Hero" showing up as the #2 recommendation for the High-Energy Pop user even though that user asked for "happy" music and Gym Hero's mood is "intense." This happens because Gym Hero matches on genre (pop, +1.0) and has near-perfect energy (0.93 vs target 0.88, +1.90), giving it a total of 2.90. The mood mismatch only costs it 0.5 points — the difference between "happy" and "intense" is worth less than a 0.05 energy gap. To a listener, though, the difference between a happy pop song and an intense workout track is obvious. The system knows the numbers are close; it does not know the feelings are different.

**Weight experiments we ran:**
1. Original weights (genre 2.0, mood 1.0, energy 1.0) — genre dominated, Contradictory Vibe broken
2. Genre halved + mood removed + energy doubled (genre 1.0, energy 2.0) — fixed Contradictory Vibe but lost the ability to distinguish chill from focused
3. Final rebalanced weights (genre 1.0, mood 0.5, energy 2.0) — best overall behavior, Contradictory Vibe fixed, mood correctly breaks ties, energy drives primary ranking

See [reflection.md](reflection.md) for detailed profile-pair comparisons.

---

## 8. Future Work  

1. **Use more features in scoring.** Valence, danceability, acousticness, instrumentalness, and speechiness are already in the data but contribute nothing to the score. Adding weighted distance on these features would let the system distinguish a bright danceable pop track from a dark slow pop ballad, which it currently cannot do.

2. **Support multiple profiles per user.** Real people have a gym playlist and a study playlist. Instead of one fixed taste profile, the system could let a user define context-specific profiles ("morning commute," "late night coding") and switch between them.

3. **Strengthen diversity enforcement.** The functional API already includes a diversity-aware greedy selection mode (`diverse=True`) that penalizes repeated artists (×0.5 per repeat) and over-represented genres (3rd song in the same genre: ×0.70, 4th+: ×0.40). This reduces filter-bubble effects — a lofi listener no longer sees three lofi tracks in a row, and the system surfaces songs from adjacent genres that still match on mood and energy. The displayed score remains unpenalized so users see true match quality, and a "(diversity pick)" note flags when the penalty changed the pick order. Future improvements could add mood-level diversity (e.g., no more than two "chill" songs in a top 5) and let users tune the penalty strength.

---

## 9. Personal Reflection  

My biggest learning moment was seeing the Contradictory Vibe profile recommend a quiet piano piece to someone who wanted aggressive, high-energy music. The math was correct — genre matched, so it scored highest — but the recommendation was clearly wrong. That showed me that a scoring system can be logically sound and still produce bad results if the weights do not reflect what actually matters to a listener. The gap between "correct by the formula" and "correct by human judgment" is where bias lives.

Using AI tools helped me move faster through the mechanical parts — generating CSV data, scaffolding the scoring function, structuring the model card. But I had to double-check the weight suggestions carefully. The initial recommendation of genre at +2.0 seemed reasonable in isolation, but it took running the actual experiments across multiple profiles to see that it was too dominant. The tool gave me a starting point; the experiments told me whether it was right.

What surprised me most is how few ingredients it takes for a recommendation to "feel" real. Three signals — genre, mood, and energy distance — are enough to produce results that often match human intuition. Library Rain really does feel like the right pick for a chill lofi listener. But that same simplicity is what makes the system brittle: it only takes one edge case (a user who wants classical but aggressive) to expose that the system is pattern-matching on surface features, not understanding music.

If I extended this project, I would incorporate valence and acousticness into the scoring to capture emotional tone and sonic texture, strengthen the existing diversity penalties with mood-level constraints so the top 5 covers a wider emotional range, and experiment with letting users rate recommendations so the system could learn and adjust weights over time instead of relying on fixed ones.
