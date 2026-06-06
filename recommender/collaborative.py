import pandas as pd
from surprise import Dataset, Reader, SVD

ratings = pd.read_csv("ratings.csv")
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[["userId", "movieId", "rating"]], reader)
trainset = data.build_full_trainset()

model = SVD()
model.fit(trainset)

def predict_rating(user_id, movie_id):
    try:
        return model.predict(user_id, movie_id).est
    except Exception as e:
        print("Collaborative error:", e)
        return 0




