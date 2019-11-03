import requests

main_link = 'https://api.github.com/users/'
user_name = 'Donchenkov'

req = requests.get(f'{main_link}{user_name}/repos')

with open('gitrepos.json', 'wb') as file:
    file.write(req.content)

