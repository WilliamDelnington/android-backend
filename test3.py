import requests
import time
import pyktok as pyk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

apiKey = ""
keyword = ""

# url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&apiKey={apiKey}"

# res = requests.get(url)

# print(res.json())

# url = 'http://192.168.56.1:8000/videos'
def main():
    while True:
        try:
            driver = webdriver.Chrome(service=Service("E:\ChromeDriver\chromedriver.exe"))

            url = "https://www.tiktok.com/@emobiletech2.4/video/7430534038751939872"

            driver.get(url)

            page_source = driver.page_source

            bs = BeautifulSoup(page_source, "html.parser")
            app = bs.find("div", {"id": "app"})
            tiktokWebPlayer = app.find("div", {"class": "tiktok-web-player"})
            videoTag = tiktokWebPlayer.find("video")
            source = videoTag.find_all("source")
            if source:
                src = source[2].get("src")
            else:
                src = videoTag.get("src")
            driver.quit()
            print(src)
            if src.startswith("https://www.tiktok.com/"):
                break

        except Exception as e:
            print("Error:", e.message)


def main2(url):
    pyk.save_tiktok(url, True, "video_data.csv", 'chrome')

main2("https://www.tiktok.com/@emobiletech2.4/video/7430534038751939872")