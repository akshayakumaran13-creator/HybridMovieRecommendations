import pandas as pd

movies = pd.read_csv("movies.csv")

print(movies.head())
print()
print("Total Movies:", len(movies))
