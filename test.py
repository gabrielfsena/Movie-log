import os
import requests
from bs4 import BeautifulSoup
import time 
import re
import pandas as pd

save_path = "./Filmes/"

movie = "Master and Commander"
year = 2003
rating = 5
date = "2002-11-29"  

#status = watched, watchlist
# TEMPLATE .md Obsidian
#tags:{keywords}
#streaming:{streaming}
#trailer:{trailer}
#awards:{awards}
#{recs}
#language: {language}
#trailer: {trailer}

template = """---
status: Watched
rating: {rating}
year: {year}
date_watched: {date}
cover: {cover_url}
director: "[[{director_name}]]"
genre: 
{genre}
tags: {keywords}


---
# {name}

<div style="display: flex; justify-content: center; align-items: center; height: 100%;">  
<iframe src="{trailer}" width="560" height="315" frameborder="0" allowfullscreen></iframe>  
</div>

>[!example] Sinopse (TMDB)\n>{sinopse}

---
## Review


---
## Conexões Relacionadas
- **Filmes Similares:** 
recs here
"""

API_KEY = "a4d425773652f64ab8a16a07a16ccd7d"

base_url = "https://image.tmdb.org/t/p/w500/"  # Define o caminho base para as imagens

# Função para pegar o ID do filme
def get_id(title, year):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "primary_release_year": year,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" in data and data["results"]:
        movie_id = data["results"][0]["id"]
        return movie_id
    else:
        print("Filme não encontrado ou resultados vazios.")
        return None
    
#limpar as tags    
def limpar_tag(keyword):
    # Remove tudo que não for letra, número, espaço ou hífen
    tag = re.sub(r'[^a-zA-Z0-9\s-]', '', keyword)
    # Substitui espaços por hifens e deixa tudo minúsculo
    return tag.replace(" ", "-").lower()
 







# Gera um nome de arquivo seguro para o filme
filename = os.path.join(save_path, f"{movie}.md")

# Obtém o ID do filme da API
movie_id = get_id(movie, year)



if movie_id:


    # URLs para obter dados do filme
    movieid_link = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    url_base = f"https://api.themoviedb.org/3/movie/{movie_id}/"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    vides_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={API_KEY}"


    # Requisição para pegar os dados do filme
    response = requests.get(movieid_link)
    movie_data = response.json()

    # Obtém o caminho do poster
    poster_path = movie_data.get('poster_path')
    cover_url = base_url + poster_path if poster_path else "Poster não encontrado"
    
    # Requisição para obter os créditos do filme
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()
    
    # Encontra o diretor
    directors = [person['name'] for person in credits_data['crew'] if person['job'] == 'Director']
    director_name = ", ".join(directors)  # Junta os diretores em uma string separada por vírgulas
    
    # Encontrar os gêneros
    genres = movie_data.get('genres', [])
    genre_names = [genre['name'] for genre in genres]
    formatted_genres = "\n".join([f"- \"[[{genre_names}]]\"" for genre_names in genre_names])

    #SINOPSE
    overview = movie_data.get('overview')

    #lingua
    language = movie_data.get('original_language')

    #pegar keywords
    keywords_result = requests.get(keywords_url)
    keywords_data = keywords_result.json()
    keywords = [k['name'] for k in keywords_data['keywords']]

    # Pegar as 10 primeiras
    top_keywords = keywords[:10]
    tags_limpas = [limpar_tag(k) for k in top_keywords]







    #pegar o trailer
    videos = requests.get(vides_url)
    result = videos.json()
    trailer_video = next((video for video in result['results'] if video.get('type') == 'Trailer'), None)
    key = trailer_video.get('key')
    
    print(movie_id)
    # Escreve o arquivo .md com os dados
    with open(filename, "w", encoding="utf-8") as f:
        f.write(template.format(
            name=movie,
            rating=rating,
            year=year,
            date=date,
            director_name=director_name,
            genre=formatted_genres,
            cover_url=cover_url,
            language=language,
            sinopse =overview,
            trailer =f'https://www.youtube.com/embed/{key}?autoplay=0',
            keywords=tags_limpas
        ))