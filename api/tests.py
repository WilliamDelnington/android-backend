from django.test import TestCase
from django.urls import resolve 

# Create your tests here.
class URLTestCase(TestCase):
    def test_urls_exist(self):
        urls_to_test = [
            "/articles",
            "/articles/3",
            "/articles/search?source=Samsung",
            "/articles/uploadForm",
            "/articles/uploadUrlOnlyForm",
            "/articles/comments",
            "/articles/comments/2",
            "/articles/comments/search",
            "/articles/comments/temporary",
            "/articles/comments/temporary/4",
            "/articles/comments/temporary/search",
            "/articles/reactions",
            "/articles/reactions/3",
            "/articles/reactions/search?user=2",
            "/articles/reactions/search?articleId=8",
            "/articles/reactions/temporary",
            "/articles/reactions/temporary/3",
            "/articles/reactions/temporary/search?user=4",
            "/articles/reactions/temporary/search?articleId=43"
            "/videos",
            "/videos/15",
            "/videos/search?originKey=Samsung",
            "/videos/uploadForm",
            "/videos/uploadUrlOnlyForm",
            "/videos/comments",
            "/videos/comments/3",
            "/videos/comments/search?videoId=14",
            "/videos/comments/temporary",
            "/videos/comments/temporary/5",
            "/vidoes/comments/temporary/search?user=2",
            "/videos/reactions",
            "/videos/reactions/3",
            "/videos/reactions/search?user=3",
            "/videos/reactions/search?videoId=5",
            "/videos/reactions/temporary",
            "/videos/reactions/temporary/6",
            "/videos/reactions/temporary/search?user=2",
            "/videos/reactions/temporary/search?videoId=10",
            "/searchHistory",
            "/searchHistory/7",
            "/searchHistory/search?user=2",
            "/searchHistory/temporary",
            "/searchHistory/temporary/3",
            "/searchHistory/temporary/search?user=5",
            "/users",
            "/users/5",
            "/users/temporary"
            "/users/temporary/2"
        ]

        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(
                    response.status_code,
                    [200, 204, 201, 302, 301],
                    msg=f"URL {url} returns in status code {response.status_code}"
                )