# -*- coding: utf-8 -*-

import os
import re
import urllib2
import urllib
import logging
import base64
import json
from datetime import datetime

logging.basicConfig(filename='%s/bwgtellyou.log' % os.path.split(os.path.realpath(__file__))[0], level=logging.DEBUG,
                    format='%(asctime)s %(message)s')


def get_stock(url, pattern):
    '''
    请求搬瓦工方案并返回是否有货，有货yes，无货no
    url：请求的搬瓦工方案url
    pattern: 一个正则表达式双冒号字符串，如"Out of Stock"
    '''

    header = {"host": "bwh88.net",
              "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0"}
    req = urllib2.Request(url, None, header)
    respond = urllib2.urlopen(req).read()

    re_stock = re.compile(r"%s" % pattern)

    if re_stock.search(respond):
        return "no"
    else:
        return "yes"


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(message, subject):
    '''
    获得邮箱smtp的用户名，密码，并发送title，内容同title
    '''
    try:
        p_data = {"from": "xxx@xxx.xxx", "to": "xxxx@xxx.com", "subject": "搬瓦工VPS监控-%s" % subject,
                  "html": message}
        post_param_data = urllib.urlencode(p_data)
        request = urllib2.Request("https://api.mailgun.net/v3/xxxxx/messages")

        base64string = base64.b64encode('%s:%s' % ("api", "key-xxxxx"))
        request.add_header("Authorization", "Basic %s" % base64string)
        request.add_data(post_param_data)

        f = urllib2.urlopen(request, timeout=2)
        print
        f.read()

    except Exception, e:
        logging.warning("%s" % str(e))


#######脚本开始#######

# 定义需要监控的URL，仅一个，默认DC6-512M-500G-49.9美元的
dc6_url = "https://bwh88.net/cart.php?a=add&pid=94&aff=58257"

# 定义缺货页面验证的正则表达式，缺货会有Out of Stock字样
stock_pattern = "Out of Stock"

# 定义发送的消息，HTML格式
content = "购买地址是</br><a href=%s>点击购买DC6-49.99</a></br>BWH3HYATVBJW" % dc6_url

# 请求方案页面，获取缺货状态
status = get_stock(dc6_url, stock_pattern)
# 如果已经补货，则标题是补货成功
# 如果没有补货，则每天早上八点整发消息通知程序运行正常
if status == "yes":
    send_mail(content,"已经补货")
elif datetime.now().hour == 8 and datetime.now().minute == 0:
    send_mail("程序存货","程序存活")
else:
    logging.info("没有补货，不发送邮件")
