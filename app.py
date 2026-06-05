from flask import Flask, render_template, request
import requests
from urllib.parse import quote

app = Flask(__name__)

API_KEY = "cc832b17654beeb62e0356a132e8c424"


def search_movie(movie_name):

    url = (
        f"https://api.themoviedb.org/3/search/movie"
        f"?api_key={API_KEY}"
        f"&query={quote(movie_name)}"
    )

    data = requests.get(url).json()

    if not data["results"]:
        return None

    return data["results"][0]


def get_recommendations(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        f"?api_key={API_KEY}"
    )

    data = requests.get(url).json()

    return data.get("results", [])[:12]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    movie_name = request.form["movie"]

    movie = search_movie(movie_name)

    if movie is None:
        return "Movie not found"

    recommendations = get_recommendations(
        movie["id"]
    )

    return render_template(
        "movie.html",
        movie=movie,
        recommendations=recommendations
    )


@app.route("/movie/<int:movie_id>")
def movie_page(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={API_KEY}"
    )

    movie = requests.get(url).json()

    recommendations = get_recommendations(
        movie_id
    )

    return render_template(
        "movie.html",
        movie=movie,
        recommendations=recommendations
    )


if __name__ == "__main__":
    app.run(debug=True)