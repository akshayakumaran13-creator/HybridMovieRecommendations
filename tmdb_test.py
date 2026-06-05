import requests

API_KEY = "cc832b17654beeb62e0356a132e8c424"

url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"

response = requests.get(url)

data = response.json()

for movie in data["results"][:10]:
    print(movie["title"])