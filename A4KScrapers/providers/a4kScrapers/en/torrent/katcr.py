import threading, re

from bs4 import BeautifulSoup
from resources.lib.common import source_utils
from resources.lib.common.source_utils import serenRequests

class sources:

    def __init__(self):
        self.domain = "katcr.co"
        self.base_link = 'https://katcr.co'
        self.search_link = '/advanced-usearch/'
        self.threads = []
        self.threadResults = []
        self.session = serenRequests()

    def get_info(self, results, package):
        torrent_list = []

        for i in results:
            try:
                torrent = {}
                torrent['package'] = package
                torrent['release_title'] = i.find('a', {'class', 'torrents_table__torrent_title'}).text
                torrent['magnet'] = i.find_all('a', {'class': 'button'})[2]['href']
                size = re.findall(r'data-title="Size">(.*?)</td>', i.text)[0]
                torrent['size'] = source_utils.de_string_size(size)
                torrent['seeds'] = 0
                torrent_list.append(torrent)
            except:
                continue
        return torrent_list

    def movie(self, title, year):
        query = '%s %s' % (title, year)
        postData = {'category': 'Movies', 'orderby': 'seeds-desc', 'search': query}
        url = self.base_link + self.search_link
        response = self.session.post(url, data=postData)
        response = self.session.post(url, data=postData)
        results = BeautifulSoup(response.text, 'html.parser').find_all('tr')
        torrent_list = []

        results = self.get_info(results, 'single')
        torrent_list = []
        for torrent in results:
            try:
                if not source_utils.filterMovieTitle(torrent['release_title'], title, year):
                    continue
                torrent_list.append(torrent)
            except:
                pass
                continue
        return torrent_list

    def episode(self, simpleInfo, allInfo):
        query = ''
        postData = {'category': 'TV', 'orderby': 'seeds-desc', 'search': query}
        url = self.base_link + self.search_link
        response = self.session.post(url, data=postData)

        self.threads.append(threading.Thread(target=self.seasonPack, args=(simpleInfo, allInfo)))
        self.threads.append(threading.Thread(target=self.singleEpisode, args=(simpleInfo, allInfo)))

        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        return self.threadResults


    def seasonPack(self, simpleInfo, allInfo):

        try:
            showTitle = source_utils.cleanTitle(simpleInfo['show_title'])
            query = '%s season %s' % (showTitle, simpleInfo['season_number'])
            postData = {'category': 'TV', 'orderby':'seeds-desc', 'search': query}
            url = self.base_link + self.search_link
            response = self.session.post(url, data=postData)
            results = BeautifulSoup(response.text, 'html.parser').find_all('div',
                                                                           {'class':'torrents_table__torrent_name'})

            results = self.get_info(results, 'season')
            torrent_list = []

            for torrent in results:
                try:
                    if not source_utils.filterSeasonPack(simpleInfo, torrent['release_title']):
                        continue
                    torrent_list.append(torrent)
                except:
                    continue

            self.threadResults += torrent_list
        except:
            import traceback
            traceback.print_exc()
            pass

    def singleEpisode(self, simpleInfo, allInfo):

        try:
            showTitle = source_utils.cleanTitle(simpleInfo['show_title'])
            season = simpleInfo['season_number'].zfill(2)
            episode = simpleInfo['episode_number'].zfill(2)
            query = '%s s%se%s' % (showTitle, season, episode)
            postData = {'category': 'TV', 'orderby': 'seeds-desc', 'search': query}
            url = self.base_link + self.search_link

            response = self.session.post(url, data=postData)
            results = BeautifulSoup(response.text, 'html.parser').find_all('div',
                                                                           {
                                                                               'class': 'torrents_table__torrent_name'})
            results = self.get_info(results, 'single')
            torrent_list = []
            for torrent in results:
                try:
                    if not source_utils.filterSeasonPack(simpleInfo, torrent['release_title']):
                        continue
                    torrent_list += torrent
                except:
                    pass

            self.threadResults += torrent_list
        except:
            import traceback
            traceback.print_exc()
            pass
