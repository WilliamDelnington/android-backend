import requests
import threading

urls = [
    "https://news.samsung.com/global/samsung-brings-eclipsa-audio-3d-technology-developed-with-google-to-2025-tvs-and-soundbars",
    "https://www.apple.com/newsroom/2024/12/voice-memos-update-brings-layered-recording-to-iphone-16-pro-lineup/",
    "https://news.microsoft.com/source/features/work-life/his-own-body-weakened-by-rare-disease-gamer-adopts-stronger-one-leaves-legacy-within-world-of-warcraft/",
    "https://www.asus.com/news/fevc5ulcs1iappcd/",
    "https://www.nokia.com/about-us/news/releases/2024/12/19/nokia-and-e-uae-showcase-worlds-first-fixed-end-to-end-network-slicing-solution-for-gaming-applications/",
    "https://www.dell.com/en-vn/blog/cybersecurity-tips-we-can-learn-from-buddy-the-elf/",
    "https://www.huawei.com/en/news/2024/11/tech4all-iucn-tech4nature",
    "https://www.mi.com/global/discover/article?id=4029"
]

def check_url_status(url):
    try:
        res = requests.get(url, timeout=180)
        print(f"{url} has status code {res.status_code}")
    except Exception as e:
        print(f"{url} - Error: {e}")

threads = []
for url in urls:
    thread = threading.Thread(target=check_url_status, args=(url,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()