import requests,datetime,re
import dateutil.relativedelta
from pyquery import PyQuery

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'
}

def get_page(page,kw,start_time,end_time):
    url = 'http://search.ccgp.gov.cn/bxsearch'
    params = {
        'searchtype':1,
        'page_index':page,
        'bidSort':0,
        'pinMu':0,
        'bidType':1,
        'dbselect':'bidx',
        'kw':kw,
        'start_time':start_time,
        'end_time':end_time,
        'timeType':3,
        'pppStatus':0
    }
    with requests.get(url,headers=headers,params=params) as response:
        if response.status_code == requests.codes.ok:
            return response.text
        return None

def get_budget(url):
    with requests.get(url,headers=headers) as response:
        response.encoding = 'utf-8'
        if response.status_code == requests.codes.ok:
            # 每个页面的预算金额没有规则,不好提取
            result = re.match('.*?预算金额：(.*?)</p>.*',response.text,re.S)
            if result:
                return result.group(1)
            # doc = PyQuery(response.text)
            # budget = doc('div.vF_detail_content').children('p:nth-child(5)').text()[5:]
            # print(budget)
        return None



def parse_page(text):
    if text:
        doc = PyQuery(text)
        lis = doc('.vT-srch-result-list-bid').children('li')
        for li in lis.items():
            title = li.find('a:first-child').text()
            href = li.find('a:first-child').attr('href')
            infos = li.find('span').text().split('|')
            yield {
                'title': ''.join(title.split()),
                'href':href,
                # 'budget': get_budget(href),
                'time': infos[0],
                'purchaser': infos[1].strip()[4:],
                'agency': infos[2].strip().split('\n')[0][5:],
                'bid_type': infos[2].strip().split('\n')[1].strip(),
                'provence': infos[3],
                'pin_mu': infos[4]
            }

if __name__ == '__main__':
    end_time = datetime.datetime.now()
    start_time = end_time + dateutil.relativedelta.relativedelta(months=-1)
    text = get_page(1,'采购',start_time.strftime('%Y-%m-%d'),end_time.strftime('%Y-%m-%d'))
    for item in parse_page(text):
        print(item)