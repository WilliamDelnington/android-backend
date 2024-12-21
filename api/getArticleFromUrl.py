import requests
import traceback
from datetime import datetime
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
                            [c.text for c in contents.find_all(value[l - 1][0], value[i - 1][1]) 
                             if not c.has_attr(value.get("excludeCondition"))])
                    else:
                        content = "\n".join(
                            [c.text for c in contents.find_all(value[l - 1][0], value[i - 1][1])]
                        )
                
            if not articleDate:
                articleDate = datetime.now()
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
        ],
        title = [
            ("article", {"id": "content"}),
            ("div", {"class": "duet--article--lede"}),
            ("div", {"class": "flex"}),
            ("h1", {})
        ],
        description = [
            ("article", {"id": "content"}),
            ("div", {"class": "duet--article--lede"}),
            ("div", {"class": "flex"}),
            ("h2", {})
        ],
        content = [
            ("article", {"id": "content"}),
            ("div", {"class": "duet--article--article-body-component-container"}),
            ("div", {"class": "duet--article--article-body-component"})
        ]
    )

def get_gizmodo_com_article_content(url: str):
    return get_article_content(
        url,
        "gizmodo.com-",
        articleId = [
            ("article", {}),
            ("time", {})
        ],
        author = [
            ("article", {}),
            ("a", {"rel": "author"}),
        ],
        urlToImage = [
            ("article", {}),
            ("div", {"class": "featured"}),
            ("figure", {"id": "attachment_featured"}),
            ("img", {})
        ],
        title = [
            ("article", {}),
            ("header", {}),
            ("h1", {})
        ],
        description = [
            ("article", {}),
            ("header", {}),
            ("div", {"class": "post-excerpt"})
        ],
        content = [
            ("article", {}),
            ("div", {"class": "entry-content"}),
            ("p", )
        ])

def get_digital_trends_article_content(url: str):
    return get_article_content(
        url,
        "digital-trends-",
        articleId = [
            ("div", {"id": "h-maincontent"}),
            ("div", {"class": "b-page__inner"}),
            ("div", {"class": "b-headline__meta"}),
            ("time", {})
        ],
        author = [
            ("div", {"id": "h-maincontent"}),
            ("div", {"class": "b-page__inner"}),
            ("div", {"class": "b-headline__meta"}),
            ("span", {"class": "b-byline__authors"}),
            ("a", {"rel": "author"})
        ],
        urlToImage = [
            ("div", {"id": "h-maincontent"}),
            ("div", {"class": "b-page__inner"}),
            ("div", {"class": "b-single__inner"}),
            ("figure", {}),
            ("img", {})
        ],
        title = [
            ("div", {"id": "h-maincontent"}),
            ("div", {"class": "b-page__inner"}),
            ("header", {"class": "b-headline"}),
            ("h1", {"class": "b-headline__title"})
        ],
        content = [
            {"div", {"id": "h-maincontent"}},
            ("div", {"class": "b-page__inner"}),
            ("div", {"class": "b-single__inner"}),
            ("article", {"class": "b-content"}),
            ("p", {})
        ]
    )

def get_pcworld_article_content(url: str):
    return get_article_content(
        url,
        "pcworld-",
        author = [
            ("main", {"id": "primary"}),
            ("article", {"class": "post"}),
            ("header", {}),
            ("div", {"class": "entry-meta"}),
            ("div", {"class": "meta-text"}),
            ("div", {"class": "meta-text-top"}),
            ("span", {"class": "author"})
        ],
        urlToImage = [
            ("main", {"id": "primary"}),
            ("article", {"class": "post"}),
            ("section", {}),
            ("")
        ]
    )