from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup


class Navigator(object):

    def __init__(self, url, agent):
        self.agent = agent
        self.parsed_url = urlparse(url)
        self.headers = {'User-Agent': self.agent}
        self._load_page(self.parsed_url.geturl())
        self._initialize_soup()
        self._update_links()

    def _load_page(self, url):
        self.page = requests.get(
            url=url,
            headers=self.headers
        )

    def _initialize_soup(self):
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def _update_links(self):
        self.links = list()
        for div in self.soup.select('div[class*="browse_list_wrapper"]'):
            self.links += [a_tag['href'] for a_tag in div.find_all('a', class_='title', href=True)]

    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        try:
            link = self.links[self.counter]
            self.counter += 1
            return self._get_url(link)
        except IndexError:
            if self._has_next_page():
                self._load_page(self._next_page)
                self._initialize_soup()
                self._update_links()
                self.counter = 0
                return self.__next__()
            else:
                raise StopIteration

    def _has_next_page(self):
        found = True
        a_tag = self.soup.find('a', class_='action', rel='next')
        if a_tag is not None:
            self._next_page = self._get_url(a_tag['href'])
        else:
            found = False
        return found

    def _get_url(self, path):
        root = self.parsed_url.scheme + '://' + self.parsed_url.netloc
        return urljoin(root, path)
