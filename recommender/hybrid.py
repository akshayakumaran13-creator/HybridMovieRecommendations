import pandas as pd

from recommender.content_based import recommend_movies

movies = pd.read_csv("movies.csv")

def hybrid_recommend(movie_title):

    recommendations = recommend_movies(
        movie_title
    )

    return recommendations