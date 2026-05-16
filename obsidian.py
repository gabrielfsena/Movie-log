import os
import pandas as pd
import requests
import time
import re
import math

data_path = "../data/"
save_path = "../Filmes"

# Cria pasta se não existir
os.makedirs(save_path, exist_ok=True)

# TEMPLATE .md Obsidian
template = """---
status: Watched
rating: {rating}
year: {year}
date_watched: {date}
language: {language}
cover: {cover_url}
director: "[[{director_name}]]"
genre:
{genre}
tags: {keywords}
---

# {name}

<div style="display: flex; justify-content: center; align-items: center;">
<iframe src="{trailer}" width="560" height="315" frameborder="0" allowfullscreen></iframe>
</div>

>[!example] Sinopse (TMDB)
>{sinopse}

---
## Review

---

## Conexões Relacionadas
- **Filmes Similares:**
"""


API_KEY = os.getenv("TMDB_API_KEY")

base_url = "https://image.tmdb.org/t/p/w500/"

# Carregar CSVs
df_watched = pd.read_csv(os.path.join(data_path, "watched.csv"))
df_ratings = pd.read_csv(os.path.join(data_path, "ratings.csv"))

# Merge
merged_df = pd.merge(
    df_watched,
    df_ratings[['Name', 'Rating']],
    on='Name',
    how='inner'
)

# Buscar ID do filme
def get_id(title, year):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "primary_release_year": year,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("results"):
        return data["results"][0]["id"]
    return None


# Limpar tags para Obsidian
def limpar_tag(keyword):
    tag = re.sub(r'[^a-zA-Z0-9\s-]', '', keyword)
    return tag.replace(" ", "-").lower()


# Loop principal
for _, row in merged_df.iterrows():

    name = row["Name"]
    year = row["Year"]
    rating = row["Rating"]

    
    filename = os.path.join(save_path, f"{name}.md")

    movie_id = get_id(name, year)

    if not movie_id:
        print(f"Filme não encontrado: {name}")
        continue

    # URLs
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={API_KEY}"

    # Dados principais
    movie_data = requests.get(movie_url).json()

    # Poster
    poster_path = movie_data.get('poster_path')
    cover_url = base_url + poster_path if poster_path else "Poster não encontrado"

    # Diretor
    credits_data = requests.get(credits_url).json()
    directors = [
        person['name']
        for person in credits_data.get('crew', [])
        if person['job'] == 'Director'
    ]
    director_name = ", ".join(directors) if directors else "Desconhecido"

    # Gêneros
    genres = movie_data.get('genres', [])
    genre_names = [g['name'] for g in genres]
    formatted_genres = "\n".join([f"- \"[[{g}]]\"" for g in genre_names])

    # Sinopse
    sinopse = movie_data.get('overview', "Sinopse não encontrada.")

    # Trailer
    videos_data = requests.get(videos_url).json()
    trailer = ""
    for video in videos_data.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer = f"https://www.youtube.com/embed/{video['key']}"
            break

    # Keywords
    keywords_data = requests.get(keywords_url).json()
    keywords_list = [k['name'] for k in keywords_data.get('keywords', [])]

    top_keywords = keywords_list[:10]
    tags_limpas = [limpar_tag(k) for k in top_keywords]
    keywords = " ".join([f"#{k}" for k in tags_limpas])


    #pegar linguagem
    language = movie_data.get('original_language')

    #RATING
    new_rating = rating*(7/5).floor()

    
    




    # Escrever arquivo
    with open(filename, "w", encoding="utf-8") as f:
        f.write(template.format(
            rating=row["Rating"],
            year=year,
            date=row.get("Date", ""),
            director_name=director_name,
            genre=formatted_genres if formatted_genres else "- Gênero não encontrado",
            cover_url=cover_url,
            sinopse=sinopse,
            keywords=keywords,
            trailer=trailer,
            name=name,
            language=language
        ))

    print(f"Criado: {filename}")

    time.sleep(0.3)

print("Filmes importados!")