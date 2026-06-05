from recommender.collaborative import predict_rating

rating = predict_rating(
    1,
    1
)

print(
    "Predicted Rating:",
    rating
)