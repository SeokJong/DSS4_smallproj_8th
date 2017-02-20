# coding=utf-8
from bs4 import BeautifulSoup
import requests
import pymongo
import json
from urllib import pathname2url


class Database(object):
    def __init__(self, db_name, collection_name):
        self.connection = pymongo.MongoClient("localhost", 27017)
        self.db = self.connection[db_name]
        self.collection = self.db[collection_name]


def load_data_kobis(page):
    kobis_key = '9375718b172e48ec27d68af7aebb4fe0'
    kobis_url = 'http://www.kobis.or.kr'
    kobis_mlist = '/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={}&itemPerPage=10000&curPage={}'.format(
        kobis_key, page)
    return requests.get(kobis_url + kobis_mlist)


def load_data_daum(name):
    daum_key = 'ca6800712ed274862ce0793b72985180'
    daum_url = u'https://apis.daum.net/contents/movie?apikey={}&q={}&output=json'.format(daum_key, name)
    print(daum_url)
    return requests.get(daum_url)


class Mojo(object):
    def __init__(self):
        self.base_url = u'http://www.boxofficemojo.com'
        self.url = u''
        pass

    def get_yearly_dom(self, page, year):
        self.url = self.base_url + \
                   u'yearly/chart/?page={}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(page, year)
        return requests.get(self.url)

    def get_yearly_intl(self, year):
        self.url = self.base_url + u'yearly/chart/?view2=worldwide&yr={}&p=.htm'.format(year)
        return requests.get(self.url)

    def get_movie_intl(self, m_id):
        self.url = self.base_url + u'{}&page=intl'.format(m_id)
        return requests.get(self.url)


def load_json():
    fp = open("movie.json", "r")
    resource = json.load(fp)
    return resource


# 네이버 api 영화검색, Mname과 release_kor가 있는 dict를 찾아서 네이버 검색결과 반환
def search_naver_movie(imov):
    keyword = imov['Mname']
    enc_text = pathname2url(keyword)
    url = "https://openapi.naver.com/v1/search/movie?query=" + enc_text  # json 결과
    #    print url
    headers = {'X-Naver-Client-Id': "4o3GICRV4DheCATOr_oj", 'X-Naver-Client-Secret': "qx1velboFy"}
    response = requests.get(url, headers=headers)
    result = json.loads(response.content)
    if result['total'] == 0:
        return 'None'
    elif result['total'] == 1:
        return result['items']
    else:
        match = []
        for i in result['items']:
            if i['subtitle'] == "<b>{}</b>".format(imov['Mname']):
                match.append(i)
        if len(match) == 0:
            for i in result['items']:
                if i['pubDate'][-2:] == imov['realease_kor'][-2:]:
                    match.append(i)
                    # print i['pubDate'], imov['realease_kor'][-2:]
        elif len(match) != 1:
            for i in match:
                if i['pubDate'][-2:] == imov['realease_kor'][-2:]:
                    match = [i]
                    break
        return match[0]


# url 페이지 가져오기
def get_naver_movie(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


# 장르!, bs로 파싱한 데이터를 넣고 장르로 된 리스트를 받음
def get_genre(soup):
    hyperlinks = soup.find_all('a')
    set_genre = set()
    for i in hyperlinks:
        try:
            if i.attrs['href'].rfind('genre') != -1:
                set_genre.add(i.get_text())
        except:
            pass
    return list(set_genre)

a = Mojo()
res = a.get_movie_intl(2015)
bs_obj = BeautifulSoup(res)
