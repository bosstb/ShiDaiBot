#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import time
import thread
import ShiDaiAPI


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
                        thread.start_new_thread(self.pushtest(msg))
                        self.push_thread = 1
                        


    def pushtest(self, msg):
        record = []
        info_record = {}
        last_info = 0
        while True:
            info = []
            #获取当前所有币总的交易信息
            items = json.loads(ShiDaiAPI.getAllPairs())
            print items
            #有4次以上的记录开始判断
            if len(record) >= 3 and len(record)%3 == 0:
                #循环判断每个币的涨、跌幅
                for item in items:
                    #print items.get(item).get("ticker").get("buy")
                    now = items.get(item).get("ticker").get("last")
                    last = record[len(record) - 3].get(item).get("ticker").get("last")
                    av = (float(now) - float(last)) / float(last)
                    if info_record.get(item):
                        last_info = info_record.get(item).get("ticker").get("last")
                        last_av = (now - last_info) / now
                        if abs(last_av) >= 0.028:
                            info.append('!!!!!!!!' + item + ": Now:[" + str(now) + "] last Alarm:[" + str(last_info) + "] Change:[" + str(
                                "%.2f%%" % (last_av * 100)) + "]--------!!!!!!!!")
                            info_record[item] = items.get(item)
                    if abs(av) >= 0.01 and now != last_info:
                        #记录上次涨幅大于3%的需要关注的记录
                        info_record[item] = items.get(item)
                        #组成发送信息
                        info.append(item + ": Now:[" + str(now) + "] 30sec ago:[" + str(last) + "] Change:[" + str("%.2f%%" % (av * 100)) + "]--------")

            #记录数据
            record.append(items)
            if len(info) > 0:
                print info
                #发送信息
                self.send_msg_by_uid(str(info), msg['user']['id'])
            #15秒更新一次数据
            time.sleep(15)






def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()

