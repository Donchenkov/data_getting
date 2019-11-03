import requests

main_link = 'https://api.themoviedb.org/3/movie/top_rated'
params = {'api_key': '9ef48a3d2791c345cd3f026f6a1c27fe'}

req = requests.get(main_link, params=params)

with open('top_rated_movies.json', 'wb') as file:
    file.write(req.content)

