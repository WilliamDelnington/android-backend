import pyktok as pyk
import argparse

# class TiktokVideoDownloader:
#     def __init__(self, url):
#         self.url = url

#     def download(self):
#         pyk.specify_browser("chrome")

#         pyk.save_tiktok(
#             self.url,
#             True,
#             'data.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    
    pyk.specify_browser("chrome")
    pyk.save_tiktok(
        args.url,
        True,
        'data.csv')