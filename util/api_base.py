import json
import urllib.parse

import requests
from bs4 import BeautifulSoup


class APIBase:
    def parse(self, response):
        raise NotImplementedError()

    def get_url_with_params(self, **kwargs):
        raise NotImplementedError()

    def execute(self, **kwargs):
        url = self.get_url_with_params(**kwargs)
        r = requests.get(url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('raise_for_status : {}'.format(e))
            if e.response.status_code == 404:
                return None
            raise e
        except Exception as e:
            print('raise_for_status : {}'.format(e))
            raise e

        soup = BeautifulSoup(r.content, "html.parser")
        response = json.loads(soup.string)
        return self.parse(response)

    def post(self, payload, **kwargs):
        url = self.get_url_with_params(**kwargs)
        r = requests.post(url, json=payload)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('raise_for_status : {}'.format(e))
            if e.response.status_code == 404:
                return None
            raise e
        except Exception as e:
            print('raise_for_status : {}'.format(e))
            raise e

        soup = BeautifulSoup(r.content, "html.parser")
        response = json.loads(soup.string)
        return self.parse(response)

    def query(self, mutation, **kwargs):
        url = self.get_url_with_params(**kwargs)
        r = requests.post(url, json={'query': mutation})
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('raise_for_status : {}'.format(e))
            if e.response.status_code == 404:
                return None
            raise e
        except Exception as e:
            print('raise_for_status : {}'.format(e))
            raise e

        soup = BeautifulSoup(r.content, "html.parser")
        response = json.loads(soup.string)
        return self.parse(response)

    @classmethod
    def make_query_dict(self, **kwargs):
        d = dict()
        for arg in kwargs:
            value = kwargs[arg]
            if value:
                d.update([(arg, value)])
        return d

    @classmethod
    def make_url(self, url, query_dict):
        query_string = urllib.parse.urlencode(query_dict)
        return url + (('?' + query_string) if query_string else '')
