import requests
from bs4 import BeautifulSoup
import math
import random
from .get_proxies import get_proxies

s = requests.session()

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br'
}

proxies = []

def page_request(page, asin):

    global proxies

    if len(proxies) == 0:
        proxies = get_proxies()

    url = 'https://www.amazon.com/product-reviews/{}/ref=cm_cr_getr_d_paging_btm_next_8?ie=UTF8&reviewerType=all_reviews&pageNumber={}'

    while True:
        try:
            pos = random.randrange(len(proxies))
            r = s.get(url.format(asin, page),headers = headers, proxies = {'http':proxies[pos],'https':proxies[pos]}, timeout=8)
        except:
            try:
                proxies.pop(pos)
                continue
            except:
                proxies = get_proxies()
                continue

        # print(r.status_code)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content,'lxml')
            comentarios = soup.find_all('div', attrs = {'class':'a-section review aok-relative'})
            
            if len(comentarios)<=0:
                try:
                    proxies.pop(pos)
                    continue
                except:
                    proxies = get_proxies()
                    continue
        else:
            try:
                proxies.pop(pos)
                continue
            except:
                proxies = get_proxies()
                continue
        
        break
    
    return soup

def scrape_reviews(asins: list):

    global proxies
    proxies = get_proxies()

    for asin in asins:

        soup = page_request(1, asin)

        total_reviews = soup.find('div', attrs={'data-hook':'cr-filter-info-section'}).text.strip()
        total_reviews = total_reviews.split('|')[1].strip().split(' ')[0].strip().replace(',','')

        pages = math.ceil(float(total_reviews)/10)

        for page in range(1,pages+1)[:500]:

            if page != 1:
                soup = page_request(page, asin)

            with open('project/files/amazon/raw_data/{}_{}.html'.format(asin, page), 'w', encoding='utf8') as f:
                f.write(soup.prettify())
                print("FILE CREATED")