import requests

apiKey = ""
keyword = ""

# url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&apiKey={apiKey}"

# res = requests.get(url)

# print(res.json())

url = 'http://192.168.56.1:8000/videos'

res = requests.get(url)

print(res.text)