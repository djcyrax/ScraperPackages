# -*- coding: utf-8 -*-

'''
    Incursion Add-on
    Copyright (C) 2016 Incursion

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

import requests
import re

from resources.lib.common import tools
from resources.lib.common import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['http://2ddl.io/']
        self.base_link = 'http://2ddl.io'
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        url = {'searchTerm': title.replace(" ", "+")}
        return url


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = tvshowtitle
        return url


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):

        season = season.zfill(2)
        episode = episode.zfill(2)

        searchterm = {'searchTerm': (url + "+s" + season + "e" + episode).replace(" ", "+"), 'title': url,
                      'epTitle': title}

        return searchterm

    def sources(self, url, hostDict, hostprDict):
        links = []
        sources = []
        hostprDict = hostDict + hostprDict
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
        response = requests.get(self.base_link + self.search_link % url['searchTerm'], headers=headers)
        capture = re.findall(r'<singlelink><\/singlelink>((?s).*)Interchangeable', response.text)

        if len(capture) == 0 and 'epTitle' in url:
            response = requests.get(self.base_link + self.search_link % url['title'], headers=headers)
            capture = re.findall(r'<singlelink><\/singlelink>((?s).*)<download><\/download>', response.text)
            for i in capture:
                links.append(re.findall(r'href="(.*?)"', i))

            links = [item for sublist in links for item in sublist]

            for i in capture:
                for link in links:
                    if not any(ext in i for ext in ['.rar', '.rar.']):
                        if url['title'].lower().replace(' ','.') not in link.lower():

                            continue

                        if url['epTitle'].lower().replace(' ', '.') in link.lower():
                            for h in hostprDict:
                                if h in link:
                                    quality = source_utils.getQuality(source_utils.cleanTitle(link))
                                    video = {}
                                    video['url'] = link
                                    video['quality'] = quality
                                    video['source'] = h
                                    video['debridonly'] = True
                                    video['language'] = 'en'
                                    video['info'] = ''
                                    video['direct'] = False
                                    sources.append(video)


        else:
            for i in capture:
                links.append(re.findall(r'href="(.*?)"', i))

            links = [item for sublist in links for item in sublist]

            for i in links:
                for h in hostprDict:
                    if h in i:
                        if not any(ext in i for ext in ['.rar', '.rar.']):
                            quality = source_utils.getQuality(source_utils.cleanTitle(i))
                            video = {}
                            video['url'] = i
                            video['quality'] = quality
                            video['source'] = h
                            video['debridonly'] = True
                            video['language'] = 'en'
                            video['info'] = ''
                            video['direct'] = False
                            sources.append(video)

        return sources

    def resolve(self, url):
        return url