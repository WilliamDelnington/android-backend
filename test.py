import requests

url = "https://android-backend-tech-c52e01da23ae.herokuapp.com/videos"

url2 = "http://52.63.245.238:8000/videos"

res = requests.get(url2)

print(res.content)