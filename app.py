from flask import Flask, render_template, request
import requests
from urllib.parse import quote
from difflib import get_close_matches

app = Flask(__name__)

API_KEY = "4749b5af1a6dd90be4e054dc4be6e362"


# ----------------------------
# GET MOVIE DETAILS
# ----------------------------
def get_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    return requests.get(url).json()


# ----------------------------
# GENRES FROM MOVIE
# ----------------------------
def get_genres(movie):
    return [g["name"] for g in movie.get("genres", [])]


# ----------------------------
# SPELLING SAFE SEARCH
# ----------------------------
def search_movie(movie_name):

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(movie_name)}"
    data = requests.get(url).json()

    results = data.get("results", [])

    if not results:
        return None

    titles = [m["title"] for m in results]

    match = get_close_matches(movie_name, titles, n=1, cutoff=0.4)

    if match:
        for m in results:
            if m["title"] == match[0]:
                return m

    return results[0]


# ----------------------------
# TMDB RECOMMENDATIONS
# ----------------------------
def get_recommendations(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={API_KEY}"
    data = requests.get(url).json()

    return data.get("results", [])[:12]


# ----------------------------
# GENRE SEARCH (USER INPUT LIKE: horror, anime)
# ----------------------------
def genre_search(user_input):

    keywords = set([g.strip().lower() for g in user_input.split(",")])

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&sort_by=popularity.desc"

    data = requests.get(url).json()
    results = data.get("results", [])

    scored = []

    for m in results:

        movie = get_movie(m["id"])
        genres = set([g["name"].lower() for g in movie.get("genres", [])])

        score = len(keywords.intersection(genres))

        if score > 0:
            scored.append((m, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [m[0] for m in scored[:12]]


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# SEARCH
# ----------------------------
@app.route("/search", methods=["POST"])
def search():

    movie_name = request.form["movie"].strip()

    # -------------------------
    # CASE 1: GENRE SEARCH
    # -------------------------
    if "," in movie_name:

        recs = genre_search(movie_name)

        return render_template(
            "movie.html",
            movie={
                "title": movie_name,
                "overview": "Genre-based search results",
                "poster_path": "",
                "backdrop_path": ""
            },
            recommendations=recs,
            genres=movie_name.split(",")
        )

    # -------------------------
    # CASE 2: NORMAL MOVIE SEARCH
    # -------------------------
    movie = search_movie(movie_name)

    if not movie:
        return "Movie not found"

    movie_details = get_movie(movie["id"])

    tmdb_recs = get_recommendations(movie["id"])

    return render_template(
        "movie.html",
        movie=movie_details,
        recommendations=tmdb_recs,
        genres=get_genres(movie_details)
    )


# ------------------------
# MOVIE PAGE (CLICK NAVIGATION)
# ----------------------------
@app.route("/movie/<int:movie_id>")
def movie_page(movie_id):

    movie = get_movie(movie_id)
    recs = get_recommendations(movie_id)

    return render_template(
        "movie.html",
        movie=movie,
        recommendations=recs,
        genres=get_genres(movie)
    )


# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)