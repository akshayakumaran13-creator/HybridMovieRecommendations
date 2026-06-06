import pandas as pd
import requests
from recommender.content_based import recommend_movies
from recommender.collaborative import predict_rating

# Load MovieLens → TMDB mapping
mapping = pd.read_csv("ml_to_tmdb.csv").set_index("movieId")

def hybrid_recommend(movie_title, user_id=1, tmdb_lookup=None, api_key=None):
    score_map = {}

    # TMDB lookup
    base_match = tmdb_lookup(movie_title) if tmdb_lookup else None

    if base_match and base_match.get("id"):
        tmdb_id = base_match["id"]

        # 1. TMDB recommendations (priority)
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations?api_key={api_key}"
        data = requests.get(url).json()
        for rec in data.get("results", [])[:15]:
            tid = rec["id"]
            score_map[tid] = {
                "id": tid,
                "title": rec["title"],
                "poster_path": rec.get("poster_path"),
                "genres": rec.get("genre_ids", []),
                "score": 2.0
            }
            print(f"[CONTENT] {rec['title']} → TMDB base score")

        # 2. MovieLens boosts
        content_movies = recommend_movies(movie_title)
        for m in content_movies:
            movie_id = m["movieId"]
            if movie_id in mapping.index:
                tid = mapping.loc[movie_id]["tmdbId"]
                if tid in score_map:
                    # a) Feature similarity boost
                    score_map[tid]["score"] += 1.0
                    # b) Similar user rating boost
                    ml_score = predict_rating(user_id, movie_id) or 0
                    score_map[tid]["score"] += ml_score
                    print(f"[HYBRID] {score_map[tid]['title']} → TMDB + MovieLens boost ({ml_score:.2f})")

    else:
        # 3. Fallback → TMDB popular
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}"
        data = requests.get(url).json()
        for rec in data.get("results", [])[:15]:
            tid = rec["id"]
            score_map[tid] = {
                "id": tid,
                "title": rec["title"],
                "poster_path": rec.get("poster_path"),
                "genres": rec.get("genre_ids", []),
                "score": 1.0
            }
            print(f"[FALLBACK] {rec['title']} → TMDB popular list")

    # 4. Sort and return
    final = sorted(score_map.values(), key=lambda x: x["score"], reverse=True)
    return final[:15]











