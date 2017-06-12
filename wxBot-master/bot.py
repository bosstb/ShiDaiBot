#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import time
import thread


class TulingWXBot(WXBot):
    thread_id = ''
    push_thread = None
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    # if detail['type'] == 'at':
                        for k in my_names:
                            print my_names[k]
                            print detail['value']
                            if my_names[k] and my_names[k] in detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    reply = 'to ' + src_name + ': '
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(reply, msg['user']['id'])
                    if self.push_thread == None:
                        self.push_thread = thread.start_new_thread(self.pushtest(msg))


    def pushtest(self, msg):
        record = []
        while True:
            info = []
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
            print r.text
            items = json.loads(r.text)
            print items
            if len(record) >= 2:
                for item in items:
                    print items.get(item).get("ticker").get("buy")
                    now = items.get(item).get("ticker").get("last")
                    last = record[len(record) - 3].get(item).get("ticker").get("last")
                    av = (now - last) / last
                    if av >= 0.015:
                        info.append(item + ": 现价【" + now + "】 30秒前价【" + last + "】，波动幅度【" + av + "】--------")
            record.append(items)
            if len(info) > 0:
                print info
                self.send_msg_by_uid("info", msg['user']['id'])
            time.sleep(15)






def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()

