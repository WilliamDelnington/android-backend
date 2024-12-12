import requests

apiKey = ""
keyword = ""

url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&apiKey={apiKey}"

res = requests.get(url)

print(res.json())