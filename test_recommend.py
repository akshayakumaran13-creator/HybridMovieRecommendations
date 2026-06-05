from recommender.content_based import recommend_movies

results = recommend_movies("Toy Story")

for movie in results:
    print(movie)
    