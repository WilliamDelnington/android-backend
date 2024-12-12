import ast
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from datetime import datetime
import traceback

articleFrom = set()
brand = "Google"

database_url = "http://192.168.56.1:8000/articles/"

"""
Huawei: Slashdot.org, Quartz India, 
"""

def convert_to_valid_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = file.read()

    try:
        # Use ast.literal_eval to safely evaluate the Python-like structure
        python_dict = ast.literal_eval(data)
        
        # Convert the Python dictionary to a valid JSON string
        json_data = json.dumps(python_dict)
        
        return json_data
    except (SyntaxError, ValueError) as e:
        print("Error parsing file with ast:", e)
        return None
    
def get_article_content(
    data: dict,
    articleIdHead: str,
    hintTags: List[Tuple[str | List[str], dict]],
    excludeCondition: str | None = None
) -> dict | None:
    l = len(hintTags)
    url = data["url"]

    try:
        res = requests.get(url, timeout=100)

        if res.status_code == 200:
            bs = BeautifulSoup(res.content, "html.parser")
            post = bs.find(hintTags[0][0], hintTags[0][1])
            contents = post.find(hintTags[1][0], hintTags[1][1])
            initial = contents
            if l > 3:
                for i in range(2, l - 1):
                    try:
                        contents = contents.find(hintTags[i][0], hintTags[i][1])
                    except AttributeError as e:
                        print(f"Error parsing content: {traceback.print_exc(e)}")
                        contents = initial
                        break
            if contents == None:
                print("No content")
                contents = initial
            if excludeCondition != None:
                return {
                    "articleId": articleIdHead + data["publishedAt"],
                    "contents": "\n".join([content.text for content in contents.find_all(hintTags[l - 1][0], hintTags[l - 1][1]) if not content.has_attr(excludeCondition)])
                }
            else:
                return {
                    "articleId": articleIdHead + data["publishedAt"],
                    "contents": "\n".join([content.text for content in contents.find_all(hintTags[l - 1][0], hintTags[l - 1][1])])
                }
        else:
            print(f"Get request failed in url {url}: {res.status_code}")

    except Exception as e:
        print(f"Error in url {url} with error {e}")

def get_yahoo_entertainment_article_content(data: dict):
    return get_article_content(
        data,
        "yahoo-",
        [
            ("article", {}),
            ("div", {"class": ["body", "grid"]}),
            ("p", {"class": ["yf-1pe5jgt", "break-words"]})
        ]
    )

def get_techspot_article_content(data: dict):
    return get_article_content(
        data,
        "techspot-",
        [
            ("section", {"id": "content"}),
            ("div", {"class": "articleBody"}),
            ("p", {})
        ]
    )

def get_quartz_india_article_content(data: dict):
    return get_article_content(
        data,
        "qz-",
        [
            ("main", {"class": "sc-11qwj9y-1"}),
            ("div", {"class": "sc-r43lxo-1"}),
            ("p", {"class": "fnnahv"})
        ]
    )

def get_phonearena_article_content(data: dict):
    return get_article_content(
        data,
        "phonearena-",
        [
            ("article", {}),
            ("div", {"class": "content-body"}),
            ("div", {})
        ]
    )

def get_ubergizmo_article_content(data: dict):
    return get_article_content(
        data,
        "ubergizmo-",
        [
            ("div", {"id": "skincontainer_content"}),
            ("div", {"class": "content"}),
            ("p", {})
        ]
    )

def get_android_authority_article_content(data: dict):
    return get_article_content(
        data,
        "android-authority-",
        [
            ("main", {"class": "d_B d_o"}),
            ("div", {"class": "d_ae d_A"}),
            ("div", {"class": "d_e d_X"})
        ]
    )

def get_android_central_article_content(data: dict):
    return get_article_content(
        data,
        "android-central-",
        [
            ("article", {"class": "article"}),
            ("section", {"class": "content-wrapper"}),
            ("div", {"id": "article-body"}),
            ("p", {})
        ]
    )

def get_phandroid_article_content(data: dict):
    return get_article_content(
        data,
        "phandroid-",
        [
            ("article", {"class": "post"}),
            ("div", {"class": "single-body"}),
            {["p", "h2"], {}}
        ]
    )

def get_digital_trends_article_content(data: dict):
    return get_article_content(
        data,
        "digital-trends-",
        [
            ("div", {"class": "b-page__inner"}),
            ("article", {"class": "b-content"}),
            ("p", {})
        ]
    )

def get_android_police_article_content(data: dict):
    return get_article_content(
        data,
        "android-police-",
        [
            ("article", {"class": "article"}),
            ("section", {"id": "article-body"}),
            (["p", "h2", "h3"], {})
        ]
    )

def get_neowin_article_content(data: dict):
    return get_article_content(
        data,
        "neowin-",
        [
            ("section", {"class": "article"}),
            ("div", {"class": "article-content"}),
            ("p", {})
        ]
    )

def get_pc_gamer_article_content(data: dict):
    return get_article_content(
        data,
        "pc-gamer-",
        [
            ("article", {"class": "article"}),
            ("section", {"class": "content-wrapper"}),
            ("div", {"id": "article-body"}),
            ("p", {})
        ]
    )

def get_techradar_article_content(data: dict):
    return get_article_content(
        data,
        "tech-radar-",
        [
            ("article", {"class": "article"}),
            ("section", {"class": "content-wrapper"}),
            ("div", {"id": "article-body"}),
            ("p", {})
        ]
    )

def get_gsmarena_article_content(data: dict):
    return get_article_content(
        data,
        "gsmarena-",
        [
            ("div", {"id": "wrapper"}),
            ("div", {"id": "body"}),
            ("div", {"id": "review-body"}),
            ("p", {})
        ]
    )

def get_cnet_article_content(data: dict):
    return get_article_content(
        data,
        "cnet-",
        [
            ("main", {"class": "c-layoutDefault_page"}),
            ("div", {"class": "c-pageArticle"}),
            ("div", {"section": "article-body"}),
            ("div", {"class": "c-pageArticle_body"}),
            ("div", {"class": "c-pageArticle_content"}),
            ("p", {})
        ],
        "class"
    )

def get_window_central_article_content(data: dict):
    return get_article_content(
        data,
        "window-central-",
        [
            ("article", {}),
            ("section", {"class": "content-wrapper"}),
            ("div", {"id": "article-body"}),
            ("p", {})
        ]
    )

def get_the_verge_article_content(data: dict):
    return get_article_content(
        data,
        "the-verge-",
        [
            ("article", {"id": "content"}),
            ("div", {"class": "duet--article--article-body-component-container"}),
            ("p", {"class": "duet--article--standard-paragraph"})
        ]
    )

def get_gizmodo_com_article_content(data: dict):
    return get_article_content(
        data,
        "gizmodo.com-",
        [
            ("article", {"class": "post"}),
            ("div", {"class": "entry-content"}),
            ("p", {})
        ]
    )

# Usage example
file_path = 'data.txt'
data = json.loads(convert_to_valid_json(file_path))

def main():
    for i in range(len(data[brand])):
        sourceName = data[brand][i]['source']['name']
        match sourceName:
            case "Neowin":
                articleData = get_neowin_article_content(data[brand][i])
            case "Android Authority":
                articleData = get_android_authority_article_content(data[brand][i])
            case "PC Gamer":
                articleData = get_pc_gamer_article_content(data[brand][i])
            case "Android Police":
                articleData = get_android_police_article_content(data[brand][i])
            case "Ubergizmo":
                articleData = get_ubergizmo_article_content(data[brand][i])
            case "Digital Trends":
                articleData = get_digital_trends_article_content(data[brand][i])
            case "Phandroid":
                articleData = get_phandroid_article_content(data[brand][i])
            case "PhoneArena":
                articleData = get_phonearena_article_content(data[brand][i])
            case "Quartz India":
                articleData = get_quartz_india_article_content(data[brand][i])
            case "Yahoo Entertainment":
                articleData = get_yahoo_entertainment_article_content(data[brand][i])
            case "TechSpot":
                articleData = get_techspot_article_content(data[brand][i])
            case "TechRadar":
                articleData = get_techradar_article_content(data[brand][i])
            case "GSMArena.com":
                articleData = get_gsmarena_article_content(data[brand][i])
            case "Window Central":
                articleData = get_window_central_article_content(data[brand][i])
            case "CNET":
                articleData = get_cnet_article_content(data[brand][i])
            case "The Verge":
                articleData = get_the_verge_article_content(data[brand][i])
            case "Gizmodo.com":
                articleData = get_gizmodo_com_article_content(data[brand][i])
            case "Android Central":
                articleData = get_android_central_article_content(data[brand][i])
            case _:
                articleData = None

        if articleData != None:
            d = {
                "articleUniqueId": articleData.get("articleId"),
                "articleBrandType": brand,
                "sourceName": data[brand][i]["source"]["name"],
                "author": data[brand][i]["author"],
                "title": data[brand][i]["title"],
                "description": data[brand][i]["description"],
                "url": data[brand][i]["url"],
                "urlToImage": data[brand][i]["urlToImage"],
                "publishedAt": datetime.strptime(data[brand][i]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").isoformat(),
                "content": articleData.get("contents")
            }
            print(datetime.strptime(data[brand][i]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").isoformat())
            try:
                res = requests.post(database_url, json=d)
                print(f"Successfully push data into database: {data[brand][i]['url']}: {res.status_code}")
            except Exception as e:
                print(f"Error pushing data into database: {e}")
        else:
            print(f"Failed To Parse Data from {data[brand][i]['url']}")

def main2():
    for i in range(len(data[brand])):
        sourceName = data[brand][i]['source']['name']

        url = data[brand][i]['url']
        try:
            res = requests.get(url, timeout=100)

            print(f"News {sourceName} with url {url} has status {res.status_code}")
        except Exception as e:
            print(f"Error getting content in url {url}: {e}")

main()