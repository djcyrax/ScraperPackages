# -*- coding: utf-8 -*-

'''
    Incursion Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#import re, urllib, urlparse, json, sys, threading

import requests, threading, traceback, json
from bs4 import BeautifulSoup
from resources.lib.common import source_utils
from resources.lib.common import cfscrape
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'scnsrc.me'
        self.base_link = 'https://www.scnsrc.me/'
        self.search_link = 'https://www.scnsrc.me/?s=%s&x=0&y=0'
        self.threads = []
        self.link_list = []
        self.cfscraper = cfscrape.create_scraper()
        self.headers = {'Host':'www.scnsrc.me', 'Referer':self.base_link,
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}

    def moviePostThread(self, url, title):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        anchors = soup.findAll('a')
        for anchor in anchors:
            try:
                href = anchor['href']
                if '.rar.' in href or href.endswith('.rar'):
                    continue
                if title.lower().replace(' ', '.') in href.lower():
                    self.link_list.append(href)
            except:
                return

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = '%s %s' % (title, year)
            search_url = self.search_link + "?phrase=%s" % query
            response = json.loads(requests.get(search_url).text)
            post_list = []
            link_list = []
            for i in response['results']:

                post_title = i['post_title'].lower()
                if post_title.startswith(title.lower()):
                    if year in post_title:
                        post_list.append('http://' + i['domain'] + '/' + i['post_name'] + "/")

            for i in post_list:
                self.threads.append(threading.Thread(target=self.moviePostThread, args=(i,title)))

            for i in self.threads:
                i.start()

            for i in self.threads:
                i.join()

            return self.link_list
        except:
            traceback.print_exc()
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            season = season.zfill(2)
            episode = episode.zfill(2)
            season_query = "s%se%s" % (season, episode)
            query = "%s %s" % (url['tvshowtitle'], season_query)

            search_url = self.search_link % quote_plus(query)
            response = self.cfscraper.get(search_url, headers=self.headers).text

            post_list = BeautifulSoup(response, 'html.parser')
            post_list = post_list.find_all('div', {'class':'post'})
            link_list = []
            for i in post_list:
                post_link = i.find('a')['href']
                link_list = []
                response = self.cfscraper.get(post_link, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                for anchor in soup.findAll('a'):
                    if 'part' in anchor['href']:
                        continue
                    try:
                        href = anchor['href']
                        if '.rar.' in href or href.endswith('.rar'):
                            continue
                    except KeyError:
                        continue

                    if url['tvshowtitle'].lower().replace(' ', '.') in href.lower():
                        if season_query in href.lower():
                            link_list.append(href)
                        elif title.lower().replace(' ', '.') in href.lower():
                            link_list.append(href)

            filtered_list = []
            for i in link_list:
                check = False
                for f in filtered_list:
                    if f == i:
                        check = True
                if check == False:
                    filtered_list.append(i)
            return filtered_list

        except:
            traceback.print_exc()
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if url is None: return

        hostDict = hostDict + hostprDict

        for href in url:
            for host in hostDict:
                if host in href:
                    quality = source_utils.getQuality(source_utils.cleanTitle(href))
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': href, 'info': '',
                            'direct': False, 'debridonly': True})

        return sources

    def resolve(self, url):
        return url



