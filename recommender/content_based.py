import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

movies = pd.read_csv("movies.csv")
movies["genres"] = movies["genres"].fillna("")

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["genres"])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

indices = pd.Series(movies.index, index=movies["title"].str.lower()).drop_duplicates()

def recommend_movies(movie_title, top_n=20):
    query = movie_title.strip().lower()
    if query in indices:
        idx = indices[query]
    else:
        titles = movies["title"].dropna().str.lower().tolist()
        match = get_close_matches(query, titles, n=1, cutoff=0.4)
        if not match:
            return []
        idx = indices[match[0]]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i, score in sim_scores[1:top_n+1]:
        rec = movies.iloc[i]
        recommendations.append({
            "movieId": rec["movieId"],
            "title": rec["title"],
            "genres": rec["genres"]
        })
    return recommendations

