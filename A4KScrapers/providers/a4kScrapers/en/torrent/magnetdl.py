import threading, requests, re

from bs4 import BeautifulSoup
from resources.lib.common import tools
from resources.lib.common import source_utils

class sources:

    def __init__(self):
        self.domain = "magnetdl.com"
        self.base_link = 'http://www.magnetdl.com/'
        self.threads = []
        self.threadResults = []

    def getList(self, url):
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Host': 'www.magnetdl.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
        response = requests.get(url, headers=headers)
        results = BeautifulSoup(response.text, 'html.parser')
        results = results.find_all('tr')
        return results

    def get_info(self, results, package):
        torrent_list = []

        for i in results:
            try:
                torrent = {}
                torrent['package'] = package
                torrent['magnet'] = i.find_all('a')[0]['href']
                torrent['release_title'] = re.findall(r'title="(.*?)"', str(i))[1]
                torrent['seeds'] = i.find_all('td', {'class': 's'})[0].text
                size = i.find_all('td')[5].text
                size = source_utils.de_string_size(size)
                torrent['size'] = size
                torrent_list.append(torrent)
            except:
                continue

        return torrent_list

    def movie(self, title, year):
        title = source_utils.cleanTitle(title)
        url = self.base_link + '%s/' % title[:1].lower() + ('%s-%s' % (title.lower(), year)).replace(' ', '-')
        results = self.getList(url)
        results = self.get_info(results, 'single')
        torrent_list = []
        for torrent in results:
            try:
                if not source_utils.filterMovieTitle(torrent['release_title'], title, year):
                    continue
                torrent_list.append(torrent)
            except:
                continue
        return torrent_list

    def episode(self, simpleInfo, allInfo):
        self.threads.append(threading.Thread(target=self.seasonPack, args=(simpleInfo, allInfo)))
        self.threads.append(threading.Thread(target=self.singleEpisode, args=(simpleInfo, allInfo)))
        self.threads.append(threading.Thread(target=self.showPack, args=(simpleInfo, allInfo)))

        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        return self.threadResults

    def showPack(self, simpleInfo, allInfo):

        try:
            showTitle = source_utils.cleanTitle(simpleInfo['show_title'])

            url = self.base_link + '%s/%s' % (showTitle[:1].lower(), '%s season 1-%s' % (showTitle, simpleInfo['no_seasons']))
            url = url.replace(' ', '-')
            results = self.getList(url)

            url = self.base_link + '%s/%s' % (showTitle[:1].lower(), '%s complete' % showTitle)
            url = url.replace(' ', '-')
            results += self.getList(url)

            results = self.get_info(results, 'show')
            torrent_list = []

            for torrent in results:
                try:
                    if not source_utils.filterShowPack(simpleInfo, torrent['release_title']):
                        continue
                    torrent_list.append(torrent)
                except:
                    continue

            self.threadResults += torrent_list

        except:
            pass


    def seasonPack(self, simpleInfo, allInfo):

        try:
            showTitle = source_utils.cleanTitle(simpleInfo['show_title'])

            url = self.base_link + '%s/%s' % (showTitle[:1],
                                              '%s season %s' % (showTitle, simpleInfo['season_number']))
            url = url.replace(' ', '-')
            results = self.getList(url)
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
            pass

    def singleEpisode(self, simpleInfo, allInfo):

        try:
            showTitle = source_utils.cleanTitle(simpleInfo['show_title'])
            season = simpleInfo['season_number'].zfill(2)
            episode = simpleInfo['episode_number'].zfill(2)

            url = self.base_link + '%s/%s' % (showTitle[:1],
                                              '%s s%se%s' % (showTitle, season, episode))
            url = url.replace(' ', '-')
            results = self.getList(url)
            results = self.get_info(results, 'single')
            torrent_list = []

            for torrent in results:
                try:
                    if not source_utils.filterSingleEpisode(simpleInfo, torrent['release_title']):
                        continue
                    torrent_list.append(torrent)
                except:
                    continue

            self.threadResults += torrent_list
        except:
            pass