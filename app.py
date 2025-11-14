from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# === LOAD API KEY ===
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

app = Flask(__name__)

# === HALAMAN UTAMA ===
@app.route('/')
def index():
    return render_template('index.html')

# === HALAMAN ABOUT ===
@app.route('/about')
def about():
    return render_template('about.html')

# === HALAMAN REKOMENDASI FILM ===
@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    movies = []
    message = None  # Tambahan: untuk menampilkan pesan dinamis

    # Ambil daftar genre dari TMDB
    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"
    genre_data = requests.get(genre_url).json()
    genres = genre_data.get('genres', [])

    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        min_rating = float(request.form.get('rating', 0))

        # Ambil nama genre untuk ditampilkan di pesan
        genre_name = "All"
        for g in genres:
            if str(g["id"]) == str(selected_genre):
                genre_name = g["name"]
                break

        # URL dasar discover
        discover_url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={API_KEY}&language=en-US&sort_by=popularity.desc"
        )

        # Filter genre
        if selected_genre and selected_genre != "all":
            discover_url += f"&with_genres={selected_genre}"

        response = requests.get(discover_url).json()
        movies_data = response.get('results', [])

        # Filter rating minimal
        movies = [
            {
                "title": m.get("title"),
                "rating": m.get("vote_average"),
                "overview": m.get("overview"),
                "poster": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}"
                if m.get("poster_path")
                else "https://via.placeholder.com/500x750?text=No+Image",
            }
            for m in movies_data
            if m.get("vote_average", 0) >= min_rating
        ]

        # Pesan dinamis
        if movies:
            message = f"Menampilkan {len(movies)} film untuk genre '{genre_name}' dengan rating minimal {min_rating} ⭐"
        else:
            message = f"Tidak ditemukan film dengan genre '{genre_name}' dan rating di atas {min_rating}."

    return render_template(
        "recommendation.html",
        genres=genres,
        movies=movies,
        message=message
    )

# === FITUR SMART RECOMMENDATION ===
@app.route('/smart')
def smart_recommendation():
    trending_url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    data = requests.get(trending_url).json()
    all_movies = data.get('results', [])

    smart_movies = []
    for m in all_movies:
        if m.get('vote_average', 0) >= 7.0:
            poster_path = m.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            smart_movies.append({
                "title": m.get("title") or m.get("name"),
                "overview": m.get("overview", "No overview available."),
                "rating": m.get("vote_average", 0),
                "poster": poster_url,
            })

    return render_template('smart.html', movies=smart_movies)


if __name__ == '__main__':
    app.run(debug=True)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
