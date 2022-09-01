import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from bs4 import BeautifulSoup


BASE = 'https://www.amazon.com/dp/B009IWNPXK/'

s = requests.session()

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
	'Accept': 'application/json, text/plain, */*',
	'Accept-Language': 'en',
	'Accept-Encoding': 'gzip, deflate, br',
	'Authorization': 'Basic d2ViX3YyOkVOanNuUE54NHhXeHVkODU='
}

def get_proxies():
    output_proxies = []
    
    def probar_proxy(proxy):
        try:
            r = s.get(BASE, headers=headers, timeout = 5, proxies = {'http':proxy,'https':proxy})
        except:
            return

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'lxml')
            span = soup.find('span', attrs={'id':'productTitle'})
            
            if span:
                # print(span.text.strip())
                output_proxies.append(proxy)

    def run(f, my_iter):
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(tqdm(executor.map(f, my_iter), total=len(my_iter)))
        return results

    r = s.get('https://api.proxyscrape.com/?request=displayproxies')
    proxies = r.text.split('\r\n')[:-1]

    print(len(proxies))

    run(probar_proxy,proxies)

    return output_proxies

if __name__ == '__main__':
    proxies = get_proxies()
    print(f"Proxies found: {len(proxies)}")