from flask import Flask, render_template, request, redirect, session
import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote
from difflib import get_close_matches
import pandas as pd

from models import db, User, WatchHistory
from recommender.hybrid import hybrid_recommend

# ---------------- CONFIG --------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "movieai-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)

API_KEY = "18e2cbb353f6e9e61304fb49d3566eb4"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ---------------- TMDB CACHE ----------------
tmdb_cache = {}

def cached_tmdb_lookup(movie_name):
    """Cache-enabled TMDB search"""
    if movie_name in tmdb_cache:
        return tmdb_cache[movie_name]

    query = movie_name.strip().lower()
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(query)}"
    try:
        data = requests.get(url).json()
    except Exception as e:
        print("TMDB connection error:", e)
        return None
    results = data.get("results", [])

    if not results:
        try:
            movies = pd.read_csv("movies.csv")
            titles = movies["title"].dropna().tolist()
            match = get_close_matches(movie_name, titles, n=1, cutoff=0.4)
            if match:
                corrected = match[0]
                url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(corrected)}"
                data = requests.get(url).json()
                results = data.get("results", [])
        except Exception as e:
            print("Fallback error:", e)

    if not results:
        return None

    tmdb_cache[movie_name] = results[0]
    return results[0]

def get_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    return requests.get(url).json()

def get_genres(movie):
    return [g["name"] for g in movie.get("genres", [])]

# ---------------- AUTH ROUTES ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")  # go to home after login
        return "Invalid username or password"

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        security_answer = request.form["security_answer"]

        if User.query.filter_by(username=username).first():
            return "Username already exists"

        user = User(username=username, password=password, security_answer=security_answer)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")  # redirect clears form
    return render_template("signup.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        answer = request.form["security_answer"]
        new_password = request.form["new_password"]
        user = User.query.filter_by(username=username).first()
        if user and user.security_answer == answer:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return redirect("/login")  # redirect clears form
        return "Invalid details"
    return render_template("forgot_password.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/login")

# ---------------- MAIN ROUTES -------------
@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
@login_required
def search():
    movie_name = request.form["movie"].strip()
    movie = cached_tmdb_lookup(movie_name)
    if not movie:
        return "Movie not found"

    movie_details = get_movie(movie["id"])
    history = WatchHistory(user_id=current_user.id, movie_id=movie["id"], movie_title=movie["title"])
    db.session.add(history)
    db.session.commit()

    recommendations = hybrid_recommend(
        movie_name,
        current_user.id,
        cached_tmdb_lookup,
        API_KEY
    )
    return render_template("movie.html", movie=movie_details, recommendations=recommendations, genres=get_genres(movie_details))

@app.route("/history")
@login_required
def history():
    movies = WatchHistory.query.filter_by(user_id=current_user.id).order_by(WatchHistory.id.desc()).all()
    return render_template("history.html", movies=movies, user=current_user.username)

# ------------------------
# MOVIE PAGE (CLICK NAVIGATION)
# ----------------------------
@app.route("/movie/<int:movie_id>")
@login_required
def movie_page(movie_id):
    movie = get_movie(movie_id)
    if not movie:
        return "Movie not found"

    recommendations = hybrid_recommend(
        movie.get("title", ""),
        current_user.id,
        cached_tmdb_lookup,
        API_KEY
    )
    return render_template("movie.html", movie=movie, recommendations=recommendations, genres=get_genres(movie))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
