from dataclasses import dataclass
from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime


@dataclass
class SummaryDetail:
    label: str = None
    data: str = None


class Page(object):

    def __init__(self, url, agent):
        self.agent = agent
        self.page = requests.get(
            url,
            headers={'User-Agent': self.agent}
        )
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    @staticmethod
    def _empty_scores_dict():
        return dict(
            positive=None,
            mixed=None,
            negative=None
        )

    @staticmethod
    def _clean_string(string):
        return " ".join(string.split())

    def _parse_summary_detail(self, detail) -> SummaryDetail:
        label = detail['class'][1]
        data = detail.find_all('span', class_='data')
        if data is not None:
            data = ';'.join([self._clean_string(item.text) for item in data])
        return SummaryDetail(label, data)

    @staticmethod
    def _as_int(string):
        try:
            return int(string)
        except ValueError:
            return None

    @staticmethod
    def _as_float(string):
        try:
            return float(string)
        except ValueError:
            return None


class GamePage(Page):

    def __init__(self, url, agent):
        super(GamePage, self).__init__(url, agent)

    def __product_title(self):
        div = self.soup.find('div', class_='product_title')

        if div is not None:
            title = div.find('h1')
            self.title = None if title is None else self._clean_string(title.text)
            platform = div.find('span', class_='platform')
            self.platform = None if platform is None else self._clean_string(platform.text)
        else:
            self.title = None
            self.platform = None

    def __product_details(self):
        details = self.soup.find_all('li', class_='summary_detail')
        if details is not None:
            details = [self._parse_summary_detail(detail) for detail in details]
            details = {detail.label: detail.data for detail in details if detail.data is not None}
        else:
            details = dict()

        self.__save_product_details(details)

    def __save_product_details(self, details_dict):
        keys_pairs = {
            'publisher': 'publisher',
            'release_data': 'release_date',
            'product_summary': 'summary',
            'developer': 'developer',
            'product_genre': 'genre',
            'product_rating': 'rating'
        }
        for key in keys_pairs:
            try:
                self.__setattr__(keys_pairs[key], details_dict[key])
            except KeyError:
                self.__setattr__(keys_pairs[key], None)

    def __product_scores(self):
        div = self.soup.find('div', class_='section product_scores')
        if div is not None:
            meta_score = div.find('span', itemprop='ratingValue')
            self.meta_score = None if meta_score is None else self._as_int(self._clean_string(meta_score.text))
            user_score = div.select_one("div[class*=\"metascore_w user\"]")
            self.user_score = None if user_score is None else self._as_float(self._clean_string(user_score.text))
        else:
            self.meta_score = None
            self.user_score = None

    def scrap(self):
        self.__product_title()
        self.__product_details()
        self.__product_scores()
        return self.__as_list()

    def __as_list(self):
        return [
            self.title,
            self.platform,
            self.meta_score,
            self.user_score,
            self.publisher,
            self.release_date,
            self.developer,
            self.genre,
            self.rating,
            self.summary
        ]

    @staticmethod
    def get_header():
        return [
            'title',
            'platform',
            'meta_score',
            'user_score',
            'publisher',
            'release_date',
            'developer',
            'genre',
            'rating',
            'summary'
        ]
