from recommender.hybrid import hybrid_recommend

movies = hybrid_recommend(
    "Toy Story"
)

for movie in movies:
    print(movie)