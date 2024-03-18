import random
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('mongodb://test:test@3.34.97.186', 27017)  
db = client.dbjungle                      


def insert_all():
    # URL을 읽어서 HTML를 받아오고,
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.daum.net/ranking/boxoffice/yearly', headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup = BeautifulSoup(data.text, 'html.parser')

    # select를 이용해서, li들을 불러오기
    movies = soup.select('#morColl > div.coll_cont > div > ol > li')
    print(len(movies))

    # movies (li들) 의 반복문을 돌리기
    for movie in movies:
        # movie 안에 a 가 있으면,
        # (조건을 만족하는 첫 번째 요소, 없으면 None을 반환한다.)
        tag_element = movie.select_one('.wrap_cont > .info_tit > a')
        if not tag_element:
            continue
        title = tag_element.text  # a 태그 사이의 텍스트를 가져오기

        # 누적 관객수를 얻어낸다. "783,567명" 과 같은 형태가 된다.
        try:
            tag_element = movie.select_one('.wrap_cont > dl:nth-child(4) > dd')
            viewers = tag_element.text
        except:
            tag_element = movie.select_one('.wrap_cont > dl:nth-child(3) > dd')
            if not tag_element or '.' in tag_element.text :
                continue
            viewers = tag_element.text

        # 영화 포스터 이미지 URL 을 추출한다.
        tag_element = movie.select_one('.wrap_thumb > a > img')
        if not tag_element:
            continue
        poster_url = tag_element['data-original-src']
        if not poster_url:
            continue

        # 개봉일 추출
        tag_element = movie.select_one('.wrap_cont > dl:nth-child(3) > dd')
        if not tag_element:
            continue
        open_date = tag_element.text
        if ',' in open_date:
            continue
        
        open_date = open_date.split('.')
        open_year = open_date[0]
        open_month = open_date[1]
        open_day = open_date[2]


        # 영화 정보 URL 을 추출한다.
        tag_element = movie.select_one('.wrap_cont > .info_tit > a')
        if not tag_element:
            continue
        info_url = tag_element['href']
        if not info_url:
            continue
        info_url = 'https://search.daum.net/search' + info_url

        # 존재하지 않는 영화인 경우만 추가한다.
        found = list(db.movies.find({'title': title}))
        if found:
            continue

        # 좋아요를 random 으로 정한다 [0, 100)
        likes = random.randrange(0, 100)
        viewers = int(viewers.replace('명','').replace(',',''))
        doc = {
            'title': title,
            'open_year': open_year,
            'open_month': open_month,
            'open_day': open_day,
            'viewers': viewers,
            'poster_url': poster_url,
            'info_url': info_url,
            'likes': likes,
            'trashed': False,
        }
        db.movies.insert_one(doc)
        print('완료: ', title, open_year, open_month, open_day, viewers, poster_url, info_url)


if __name__ == '__main__':
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    insert_all()
