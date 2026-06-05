import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("movies.csv")

movies["genres"] = movies["genres"].fillna("")

tfidf = TfidfVectorizer(stop_words="english")

tfidf_matrix = tfidf.fit_transform(
    movies["genres"]
)

cosine_sim = cosine_similarity(
    tfidf_matrix,
    tfidf_matrix
)

def recommend_movies(movie_title):

    movie_title = movie_title.lower()

    matches = movies[
        movies["title"].str.lower().str.contains(
            movie_title,
            na=False
        )
    ]

    if matches.empty:
        return []

    idx = matches.index[0]

    similarity_scores = list(
        enumerate(cosine_sim[idx])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for movie in similarity_scores[1:11]:

        recommendations.append(
            movies.iloc[movie[0]]["title"]
        )

    return recommendations