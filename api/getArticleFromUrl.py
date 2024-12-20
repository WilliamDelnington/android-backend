import requests
import traceback
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple

def get_article_content(
    url, 
    articleIdHead: str,
    **tags: Dict[str, List[Tuple[str, Dict[str, str]]]]
):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            bs = BeautifulSoup(response.content, "html.parser")
            articleId = None
            author = None
            urlToImage = None
            title = None
            description = None
            content = None
            articleDate = None
            
            for key, value in tags.items():
                l = len(value)
                contents = bs.find(value[0][0], value[0][1])
                initial = contents
                if l > 2:
                    for i in range(1, l - 1):
                        try:
                            contents = contents.find(value[i][0], value[i][1])
                        except AttributeError as e:
                            print(f"Error parsing content: {traceback.print_exc(e)}")
                            contents = initial
                            break
                if not contents:
                    contents = initial
                if key == "author":
                    author = contents.find(value[l - 1][0], value[i - 1][1]).text
                elif key == "articleId":
                    articleDate = contents.find(value[l - 1][0], value[i - 1][1]).get("datetime")
                elif key == "urlToImage":
                    urlToImage = contents.find(value[l - 1][0], value[i - 1][1]).get("src")
                elif key == "title":
                    title = contents.find(value[l - 1][0], value[l - 1][1]).text
                elif key == "description":
                    description = contents.find(value[l - 1][0], value[i - 1][1]).text
                elif key == "content":
                    if "excludeCondition" in value:
                        content = "\n".join(
                            [c.text for c in contents.find(value[l - 1][0], value[i - 1][1]) 
                             if not c.has_attr(value.get("excludeCondition"))])
                    else:
                        content = "\n".join(
                            [c.text for c in contents.find(value[l - 1][0], value[i - 1][1])]
                        )
                
            articleId = articleIdHead + articleDate
            return articleId, articleDate, author, urlToImage, title, description, content
        else:
            raise HTTPError(f"Get request failed in url {url}: {response.status_code}")
    except Exception as e:
        raise Exception(e)
    
def get_android_central_article_content(url: str):
    return get_article_content(
        url,
        'android-central-',
        articleId = [
            ("article", {"class": "article"}),
            ("div", {"class": "news-article"}),
            ("header", {}),
            ("div", {"class": "author-byline"}),
            ("span", {"class": "author-byline__date"})
        ],
        author = [
            ("article", {"class": "article"}),
            ("div", {"class": "news-article"}),
            ("header", {}),
            ("div", {"class": "author-byline"}),
            ("span", {"class": "author-byline__author-name"})
        ],
        urlToImage = [
            ("article", {"class": "article"}),
            ("div", {"id": "content"}),
            ("section", {"class": "content-wrapper"}),
            ("picture", {}),
            ("img", {})
        ],
        title = [
            ("article", {"class": "article"}),
            ("div", {"class": "news-article"}),
            ("header", {}),
            ("h1", {})
        ],
        description = [
            ("article", {"class": "article"}),
            ("div", {"class": "news-article"}),
            ("header", {}),
            ("p", {"class": "stripline"})
        ],
        content = [
            ("article", {"class": "article"}),
            ("section", {"class": "content-wrapper"}),
            ("div", {"id": "article-body"}),
            ("p", {})
        ]
    )

def get_the_verge_article_content(url: str):
    return get_article_content(
        url,
        "the-verge-",
        articleId = [
            ("article", {"id": "content"}),
            ("div", {"class": "duet--article--date-and-comments"}),
            ("time", {})
        ],
        author = [
            ("article", {"id": "content"}),
            ("p", {"class": "duet--article--article-byline"}),
            ("span", {"class": "font-medium"})
        ],
        urlToImage = [
            {"article": {"id": "content"}},
            ("figure", {"class": "duet--article--lede-image"}),
            ("img", {})
        ]
    )