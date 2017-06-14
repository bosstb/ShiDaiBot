# -*- coding: utf-8 -*-
import json
import requests
import time


def getAllPairs():
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate, sdch",
               "Accept-Language": "zh-CN,zh;q=0.8",
               "Cache-Control": "max-age=0",
               "Connection": "keep-alive",
               "Cookie": "td_cookie=18446744072279134779; __jsluid=63ba5346e2ae272361d9c35dc78c73fa; Hm_lvt_a415e666baee8f21a707412783e345bc=1496383402,1496827984,1496977503,1497254688; Hm_lpvt_a415e666baee8f21a707412783e345bc=1497258161; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=1497257283,1497257298,1497257347; Hm_lpvt_d7682ab43891c68a00de46e9ce5b76aa=1497259091",
               "Host": "api.btc38.com",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36"}
    r = requests.get(
        'http://api.btc38.com/v1/ticker.php?c=all&mk_type=cny', headers=headers)
    return r.text

getAllPairs()