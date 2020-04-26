import requests
import asyncio
import aiohttp
import nest_asyncio
from datetime import datetime, timedelta
from flask import jsonify, request, current_app as app
from ...routes import api_v2 as api

from cachetools import cached, TTLCache

from bs4 import BeautifulSoup as bs


BASE_URL = 'https://prnigeria.com/'
BASE_URL2 = 'https://emergencydigest.com/'
BASE_URL3 = 'https://punchng.com/'
PUNCH = 'https://punchng.com/all-posts/'


headers = {
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}



def check_keyword(word):
    word = word.lower()
    if 'covid' in word:
        return True
    elif 'coronavirus' in word:
        return True
    elif 'virus' in word:
        return True
    elif 'ban' in word:
        return True
    elif 'isolat' in word:
        return True
    elif 'buhari' in word:
        return True
    return False

def get_soup(url):
    res = requests.get(url, headers=headers)
    return bs(res.content, 'lxml')

def get_latest_covid_news(soup, source):
#     print(soup)
    latest = soup.find('div', class_='widget_recent_entries')
#     print(latest)
    return [{'title': news.text, 'url': news['href'], 'source': source} for news in latest.find_all('a') if check_keyword(news.text.lower())]

def get_news_detail(news_data, source):
    news_soup = bs(news_data, 'lxml')
#     print(source)
    if source == BASE_URL:
        tt = news_soup.find('div', class_='td-post-date')
        pp = tt.text.split(' ')[2:4]

        if pp[1] == 'mins':
            time = datetime.now() - timedelta(minutes = int(pp[0]))
        elif pp[1] == 'hours':
            time = datetime.now() - timedelta(hours = int(pp[0]))
        te = news_soup.find('div', class_='td-post-content')
        if te.find('img'):
            img = te.find('img')['src']
        else:
            img = ''
    elif source == BASE_URL2:
        te = news_soup.find('div', class_='td-post-content')
        if te.find('img'):
            img = te.find('img')['src']
        else:
            img = ''
        time = news_soup.find(class_='entry-date updated td-module-date')['datetime']
    elif source == BASE_URL3:
        time = news_soup.find('time')['datetime']
        img = news_soup.find('div', class_='b-lazy')['data-src']
        te = news_soup.find('div', class_='entry-content')
    
    return {'posted_at':str(time), 'img': img, 'content': ''.join([j.text for j in te.find_all('p')[1:]])}

def get_punch_news(soup, source):
#     print(soup)
    latest = soup.find('main', class_='sub-section-wrapper')
#     print(latest)
    return [{'title': news.find('h2').text, 'url': news.find('a')['href'], 'source': source } 
              for news in latest.find_all('div', class_='items')
            if check_keyword(news.find('div', class_='seg-summary').text.lower())]


# if __name__ == "__main__":
    
newsCache = {}
# @cached(cache=TTLCache(maxsize=1024, ttl=1200))
@api.route('/get-news/ng')
def get_nigerian_news():
    # return jsonify({'status': 'success', 'data': 'all_data' })
    async def make_request(session, req_data):
        async with session.get(req_data[1]['url'], headers=headers) as resp:
            if resp.status == 200:
                news = get_news_detail(await resp.text(), req_data[1]['source'])
                all_data[req_data[0]]['img'] = news['img']
                all_data[req_data[0]]['content'] = news['content']
                all_data[req_data[0]]['posted_at'] = news['posted_at']

    # async def return_soup(url):
    #     async with session.get(url, headers=headers) as resp:
    #         if resp.status == 200:
    #             all_data += await resp.text()
            

    async def main():
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[make_request(session, i) for i in enumerate(all_data)]
            )
    # async def getall(urls):
    #     async with aiohttp.ClientSession() as session:
    #         allOf = []
    #         for url in urls:
    #             if url == PUNCH:
    #                 get_punch_news
    #         res = await asyncio.gather(
    #             *[get_evry(i, session) for i in urls]
    #         )
    #         resulta = res
    #         print(res)
    #         # return [await res]
    # async def get_evry(url, session):
    #     result = session.get(url, headers=headers)
    #     if url == PUNCH:
    #         return get_punch_news(await result.text())
    #     return get_latest_covid_news(await result.text())        


    try:
        # resulta = []
        # urls = [BASE_URL, BASE_URL2, PUNCH]
        ttl = newsCache.get('time', None)
        if ttl and ttl > datetime.now():
            return jsonify({'status': 'success', 'data': newsCache['news'] })
        # if 
        all_data = []
        latest = get_soup(BASE_URL)
        latest2 = get_soup(BASE_URL2)
        latest3 = get_soup(PUNCH)
        all_data = get_latest_covid_news(latest, BASE_URL)
        all_data += get_latest_covid_news(latest2, BASE_URL2)
        all_data += get_punch_news(latest3, BASE_URL3)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())

        newsCache['time'] = datetime.now() + timedelta(minutes = 10)
        newsCache['news'] = all_data
        # loop.run_until_complete(getall(urls))
        # print(resulta)
        
        return jsonify({'status': 'success', 'data': all_data })
    except Exception as er:
        print(er)
        return jsonify({'status': 'fail', 'message': 'AN error occured'})

