import re, threading

from bs4 import BeautifulSoup
from resources.lib.common.tools import quote_plus
from resources.lib.common import source_utils, tools
from resources.lib.common.source_utils import serenRequests

class sources:

    def __init__(self):
        self.domain = "1337x.to"
        self.base_link = "https://1337x.to"
        self.search_link = "/search/%s/1/"
        self.threads = []
        self.singleThreads = []
        self.packThreads = []
        self.showPackThreads = []
        self.torrent_list = []

    def searchResults(self, response):

        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find('table', {'class': 'table-list'})
        search_results = search_results.find('tbody')
        search_results = search_results.findAll('tr')

        return search_results

    def info_thread(self, release_title, url, package):
        url = self.base_link + url
        response = serenRequests().get(url)
        torrent = {}
        torrent['release_title'] = release_title
        torrent['magnet'] = re.findall(r'href="(magnet:?.*?)"', response.text)[0]
        size = re.findall(r'<strong>Total size</strong> <span>(.*?)</span>', response.text)[0]
        torrent['size'] = source_utils.de_string_size(size)
        torrent['seeds'] = re.findall(r'<strong>Seeders</strong> <span class="seeds">(.*?)</span>', response.text)[0]
        torrent['package'] = package
        self.torrent_list.append(torrent)

    def movie(self, title, year):

        url = self.search_link % quote_plus('%s %s' % (title, year))
        url = self.base_link + url
        try:
            search_results = self.searchResults(serenRequests().get(url))
        except:
            return

        for i in search_results:
            release = i.findAll('a')[1]
            url = release['href']
            release_title = release.text
            if source_utils.filterMovieTitle(release_title, title, year):
                self.threads.append(threading.Thread(target=self.info_thread, args=(release_title, url, 'single')))

        for i in self.threads:
            i.start()
        for i in self.threads:
            i.join()

        return self.torrent_list

    def episode(self, simpleInfo, allInfo):

        self.threads.append(threading.Thread(target=self.seasonPack, args=(simpleInfo, allInfo)))
        self.threads.append(threading.Thread(target=self.singleEpisode, args=(simpleInfo, allInfo)))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        return self.torrent_list

    def singleEpisode(self, simpleInfo, allInfo):

        season = simpleInfo['season_number'].zfill(2)
        episode = simpleInfo['episode_number'].zfill(2)

        query = quote_plus(simpleInfo['show_title'] + ' s%se%s' % (season, episode))

        url = self.base_link + self.search_link % query

        try:
            search_results = self.searchResults(serenRequests().get(url))
        except:
            import traceback
            traceback.print_exc()
            return

        for i in search_results:
            release = i.findAll('a')[1]
            url = release['href']
            release_title = release.text
            if source_utils.filterSingleEpisode(simpleInfo, release_title):
                self.singleThreads.append(threading.Thread(target=self.info_thread, args=(release_title, url, 'single')))

        for i in self.singleThreads:
            i.start()
        for i in self.singleThreads:
            i.join()

        return

    def seasonPack(self, simpleInfo, allInfo):

        season = simpleInfo['season_number']

        query = quote_plus(simpleInfo['show_title'] + ' season %s' % season)

        url = self.base_link + self.search_link % query

        try:
            search_results = self.searchResults(serenRequests().get(url))
        except:
            import traceback
            traceback.print_exc()
            return

        for i in search_results:
            release = i.findAll('a')[1]
            url = release['href']
            release_title = release.text
            if source_utils.filterSeasonPack(simpleInfo, release_title):
                self.packThreads.append(threading.Thread(target=self.info_thread, args=(release_title, url, 'season')))
        for i in self.packThreads:
            i.start()
        for i in self.packThreads:
            i.join()

        return

    def show_pack(self, simpleInfo, allInfo):

        season = 1
        no_seasons = simpleInfo['no_seasons']

        query = quote_plus(simpleInfo['show_title'] + ' season %s+%s' % (season, no_seasons))

        url = self.base_link + self.search_link % query
        print(url)
        try:
            search_results = self.searchResults(serenRequests().get(url))
        except:
            import traceback
            traceback.print_exc()
            return

        for i in search_results:
            release = i.findAll('a')[1]
            url = release['href']
            release_title = release.text
            if source_utils.filterShowPack(simpleInfo, release_title):
                self.showPackThreads.append(
                    threading.Thread(target=self.info_thread, args=(release_title, url, 'show')))

        for i in self.showPackThreads:
            i.start()
        for i in self.showPackThreads:
            i.join()

        return