# -*- coding: utf_8 -*- 

import argparse
import os
import tweepy
import urllib.request
import urllib.error

#= 画像の保存先ディレクトリ
IMAGES_DIR = './images/'

#= Twitter API Key の設定
CONSUMER_KEY        = os.environ.get('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET     = os.environ.get('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY    = os.environ.get('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

#= Search Key Word
KEYWORDS = ['#艦これ版深夜の真剣お絵描き60分一本勝負']

#= 検索オプション
RETURN_PAR_PAGE = 1000
NUMBER_OF_PAGES = 100

class ImageDownloader(object):
    image_directory = IMAGES_DIR

    def __init__(self, date):
        print("ImageDownloader.__init__")
        super(ImageDownloader, self).__init__()
        self.set_twitter_api()
        self.media_url_list = []
        self.image_directory = IMAGES_DIR + date + '/'
        self.make_directory()

    def make_directory(self):
        print("ImageDownloader.make_directory")
        os.makedirs(self.image_directory, exist_ok = True)

    def run(self):
        print("ImageDownloader.run")
        for keyword in KEYWORDS:
            self.max_id = None
            for page in range(NUMBER_OF_PAGES):
                self.download_url_list = []
                self.search(keyword, RETURN_PAR_PAGE)
                for url in self.download_url_list:
                    print(url)
                    self.download(url)

    def set_twitter_api(self):
        print("ImageDownloader.set_twitter_api")
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
            self.api = tweepy.API(auth)
        except Exception as e:
            print("[-] Error: ", e)
            self.api = None

    def search(self, term, rpp):
        print("ImageDownloader.search")
        try:
            if self.max_id:
                search_result = self.api.search(q=term, rpp=rpp, max_id=self.max_id)
            else:
                search_result = self.api.search(q=term, rpp=rpp)
            for result in search_result:
                if 'media' in result.entities:
                    for media in result.entities['media']:
                        url = media['media_url_https']
                        if url not in self.media_url_list:
                            self.media_url_list.append(url)
                            self.download_url_list.append(url)
            self.max_id = result.id
        except Exception as e:
            print("[-] Error: ", e)

    def download(self, url):
        print("ImageDownloader.download")
        url_orig = '%s:orig' % url
        filename = url.split('/')[-1]
        savepath = self.image_directory + filename
        try:
            response = urllib.request.urlopen(url_orig)
            with open(savepath, "wb") as f:
                f.write(response.read())
        except Exception as e:
            print("[-] Error: ", e)

def main():
    print("main")

    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('date', help='onedraw date')
    parser.add_argument('--debug', type=str, default='false',
                        help='debug switch')
    parser.add_argument('--clean', type=str, default='false',
                        help='clean switch')
    args = parser.parse_args()

    os.makedirs(IMAGES_DIR, exist_ok=True)
    try:
        downloader = ImageDownloader(args.date)
        downloader.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
