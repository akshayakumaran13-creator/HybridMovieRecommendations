import requests

API_KEY = "cc832b17654beeb62e0356a132e8c424"

movie_name = "Avatar"

url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"

data = requests.get(url).json()

movie = data["results"][0]

poster_url = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

print("Title:", movie["title"])
print("Poster:", poster_url)