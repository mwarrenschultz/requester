from pathlib import Path
from random import choice
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import sys
import time


def get_random_proxy(proxypath='/home/mschultz/proxies.txt'):
    with open(proxypath, 'r') as infile:
        return choice([p.strip() for p in infile.readlines()])


class Requester(requests.Session):

    def __init__(self, username=None, password=None, use_proxy=False):
        super().__init__()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[413, 429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("https://", adapter)
        self.mount("http://", adapter)
        # self.headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36'
                                      '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        if username and password:
            self.auth = (username, password)

        if use_proxy:
            self.proxy = get_random_proxy()
            pproxy = 'http://' + self.proxy
            sproxy = 'https://' + self.proxy
            self.proxies = {'http': pproxy, 'https': sproxy}
        else:
            self.proxy = None

    def __repr__(self):
        return f"Requester({self.username},{self.password},{self.use_proxy})"

    def show_proxy(self):
        return self.proxy.split(':')[0]

    def download_file(self, url: str, filename: Path) -> Path:
        """
       downloads file specified by url and filename using requests session object
       :param url: str (url of file)
       :param filename: Path (pathlib.Path object)
       :return: Path
       """
        # First, check if file exists (and has content)
        if filename.exists():
            return filename
        with open(filename, 'wb') as f:
            start = time.perf_counter()
            r = self.get(url, timeout=10)
            total_length = r.headers.get('content-length')
            dl = 0
            if total_length is None:  # no content length header
                f.write(r.content)
            else:
                for chunk in r.iter_content(1024):
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / int(total_length))
                    sys.stdout.write("\r[%s%s] %s bps %s" %
                                     ('=' * done,
                                      ' ' *
                                      (50 - done),
                                      dl // (time.perf_counter() - start),
                                      filename.name))
        return filename
