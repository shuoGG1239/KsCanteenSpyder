import requests
import json
import time

sess = requests.session()

def request(method, uri, body=None, cookie=None):
    header = {"content-type": "application/json"}
    header['ks-timestamp'] = '1564659581361'
    header['ks-partner'] = 'KSPARK'
    header['ks-sign'] = '2418096feb2b76b8a7e8b57bbe91e9f7'
    header['ks-email'] = 'kspark'
    header['referer'] = 'https://servicewechat.com/wxd66bb68c8c8d2bcd/67/page-frame.html'
    header['ks-apitype'] = 'openapi'
    header['ks-branchpark'] = 'ZH_001'
    header['User-Agent'] = 'Mozilla/5.0 (Linux; Android 7.1.1; 15 Build/NGI77B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 XWEB/882 MMWEBSDK/21 Mobile Safari/537.36 MicroMessenger/6.6.7.1300(0x26060731) NetType/WIFI Language/zh_CN MicroMessenger/6.6.7.1300(0x26060731) NetType/WIFI Language/zh_CN'
    url = "https://zhweb.kingsoft.com%s" % (uri,)
    print(url)
    if cookie is not None:
        sess.cookies.update(cookie)
    r = sess.request(method, url, data=body, headers=header, verify=False)
    try:
        print(r.status_code, r.json())
    except:
        print(r.text)
    if r.status_code != 200:
        return r.status_code, r.text
    return r.status_code, r.json()


def ks_cookie():
    return {"SESSION": 'ecd73464-ca60-457c-b324-f26700e93542'}


def ks_menu(date):
    request("GET", "/mealMenu/detail?date="+date, None, ks_cookie())


if __name__ == '__main__':
    ks_menu('2019-07-01')