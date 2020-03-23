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
    elif source == BASE_URL2:
#         print()
        time = news_soup.find(class_='entry-date updated td-module-date')['datetime']
    te = news_soup.find('div', class_='td-post-content')
    if te.find('img'):
        img = te.find('img')['src']
    else:
        img = ''
    return {'posted_at':str(time), 'img': img, 'content': ''.join([j.text for j in te.find_all('p')[1:]])}



# if __name__ == "__main__":
    
@cached(cache=TTLCache(maxsize=1024, ttl=1200))
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
            

    async def main():
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[make_request(session, i) for i in enumerate(all_data)]
            )

    try:
        all_data = []
        latest = get_soup(BASE_URL)
        latest2 = get_soup(BASE_URL2)
        all_data = get_latest_covid_news(latest, BASE_URL)
        all_data += get_latest_covid_news(latest2, BASE_URL2)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        
        return jsonify({'status': 'success', 'data': all_data })
    except Exception as er:
        print(er)
        return jsonify({'status': 'fail', 'message': 'AN error occured'})
    