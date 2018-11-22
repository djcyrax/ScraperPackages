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

import re, threading, traceback, json
from bs4 import BeautifulSoup
from resources.lib.common import source_utils, tools, cfscrape

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'rlsbb.ru/'
        self.domainbackup = 'http://old.rlsbb.ru/'
        self.base_link = 'http://search.rlsbb.ru/'
        self.search_link = 'http://search.rlsbb.ru/lib/search6515260491260.php'
        self.season_query = ''
        self.threads = []
        self.link_list = []


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
                continue


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = '%s %s' % (title, year)
            search_url = self.search_link + "?phrase=%s" % query
            requests = cfscrape.CloudflareScraper().create_scraper()
            response = requests.get(search_url).text
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
            self.show_title = tvshowtitle
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            post_list = []
            season = season.zfill(2)
            episode = episode.zfill(2)
            season_query = "s%se%s" % (season, episode)
            query = "%s %s" % (url['tvshowtitle'], season_query)

            search_url = self.search_link + "?phrase=%s" % quote(query)
            requests = cfscrape.CloudflareScraper().create_scraper()
            response = requests.get(search_url).text
            response = json.loads(response)

            for i in response['results']:
                post_title = i['post_title'].lower()
                if post_title.startswith(url['tvshowtitle'].lower()):
                    if season_query.lower() in post_title:
                        post_list.append('http://' + i['domain'] + '/' + i['post_name'] + "/")

            if len(post_list) == 0:
                season_query_list = ['s%s' % season, 'season %s' % season]
                search_url = self.search_link + "?phrase=%s" % quote(url['tvshowtitle'])
                response = json.loads(requests.get(search_url).text)
                for i in response['results']:
                    post_title = i['post_title'].lower()
                    if post_title.startswith(url['tvshowtitle'].lower()):
                        for query in season_query_list:
                            if query.lower() in post_title:
                                post_list.append('http://' + i['domain'] + '/' + i['post_name'] + "/")
            link_list = []
            for i in post_list:
                response = requests.get(i)
                soup = BeautifulSoup(response.text, 'html.parser')
                for anchor in soup.findAll('a'):
                    try:
                        href = anchor['href']
                        if '.rar.' in href:
                            continue
                    except KeyError:
                        continue

                    if url['tvshowtitle'].lower().replace(' ', '.') in href.lower():
                        if season_query in href.lower():
                            link_list.append(href)
                        elif title.lower().replace(' ','') in href.lower():
                            link_list.append(href)
            return link_list
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
                    info = source_utils.getInfo(source_utils.cleanTitle(href))
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': href, 'info': info,
                            'direct': False, 'debridonly': True})

        return sources

    def resolve(self, url):
        return url
