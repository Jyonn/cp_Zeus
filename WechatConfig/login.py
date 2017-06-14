import os

from WechatConfig.models import Cookie, Header, Setting
from urllib import request, parse
import json
import random

from cp_Zeus.settings import IMG_PATH


def get_cookie(need_cookie_list=None):
    cookies = Cookie.objects.filter()
    ret = ''
    for c in cookies:
        if need_cookie_list is not None and c.key not in need_cookie_list:
            continue
        if ret != '':
            ret += '; '
        ret += c.key + '=' + c.value
    return ret


def add_cookie_from_header(headers):
    for header in headers:
        if header[0] == 'Set-Cookie':
            s = header[1]
            s = s[:s.index(';')]
            try:
                (k, v) = s.split('=', maxsplit=1)
                # print(k, v)
                Cookie.create(key=k, value=v)
            except:
                pass


def wx_login():
    need_cookie_list = ['ua_id']
    need_headers = ['Host', 'Connection', 'Origin', 'X-Requested-With', 'User-Agent', 'Accept-Encoding', 'Accept-Language']

    url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin'
    post_data = parse.urlencode({
        'username': 'Chaping321@163.com',
        'pwd': '4c83d77de6fd405ca1333a6e05c0fa71',
        'imgcode': '',
        'f': 'json'
    }).encode('utf-8')

    req = request.Request(url, post_data)

    req.add_header('Referer', 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN')
    req.add_header('Cookie', get_cookie(need_cookie_list))
    req.add_header('Accept', '*/*')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    for header in need_headers:
        v = Header.objects.get(key=header).value
        req.add_header(header, v)

    res = request.urlopen(req)
    add_cookie_from_header(res.getheaders())

    redirect_url = json.loads(res.read().decode('utf-8'))['redirect_url']
    # redirect_url = redirect_url[:redirect_url.rfind('&')]

    Setting.create('redirect_url', redirect_url)
    Cookie.create(key='noticeLoginFlag', value='1')
    res.close()


def wx_visit_page():
    need_cookie_list = ['uuid', 'bizuin', 'ticket', 'ticket_id', 'account', 'cert', 'ticket_uin', 'login_certificate',
                        'ticket_certificate', 'fake_id', 'login_sid_ticket', 'noticeLoginFlag', 'ua_id']
    need_headers = ['Host', 'Connection', 'Upgrade-Insecure-Requests', 'User-Agent', 'Accept-Language']

    url = 'https://mp.weixin.qq.com' + Setting.objects.get(key='redirect_url').value

    req = request.Request(url)
    req.add_header('Referer', 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN')
    req.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Cookie', get_cookie(need_cookie_list))
    for header in need_headers:
        v = Header.objects.get(key=header).value
        req.add_header(header, v)

    request.urlopen(req)


def wx_get_scan_image():
    need_cookie_list = ['uuid', 'bizuin', 'ticket', 'ticket_id', 'account', 'cert', 'ticket_uin', 'login_certificate',
                       'ticket_certificate', 'fake_id', 'login_sid_ticket', 'noticeLoginFlag', 'ua_id']
    need_headers = ['Host', 'Connection', 'User-Agent', 'Accept-Language']
    url = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300&rd='+str(random.randint(100, 1000))

    req = request.Request(url)
    req.add_header('Accept', 'image/webp,image/*,*/*;q=0.8')
    req.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
    req.add_header('Referer', 'https://mp.weixin.qq.com'+Setting.objects.get(key='redirect_url').value)
    req.add_header('Cookie', get_cookie(need_cookie_list))
    for header in need_headers:
        v = Header.objects.get(key=header).value
        req.add_header(header, v)

    res = request.urlopen(req)
    image_name = 'scan.jpg'
    image_path = os.path.join(IMG_PATH, image_name)
    # image_path = '/img/scan_'+str(int(time.time()))+'.jpg'
    with open(image_path, 'wb') as f:
        f.write(res.read())
    res.close()

    return image_path


def wx_check_image_scanned():
    need_cookie_list = ['uuid', 'bizuin', 'ticket', 'ticket_id', 'account', 'cert', 'ticket_uin', 'login_certificate',
                        'ticket_certificate', 'fake_id', 'login_sid_ticket', 'noticeLoginFlag', 'ua_id']
    need_headers = ['Host', 'Connection', 'X-Requested-With', 'User-Agent', 'Accept-Language']

    random_str = str(random.random())
    Cookie.create(key='random_str', value=random_str)

    url = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1&random='+random_str

    req = request.Request(url)
    req.add_header('Cookie', get_cookie(need_cookie_list))
    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('Referer', 'https://mp.weixin.qq.com'+Setting.objects.get(key='redirect_url').value)
    req.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
    for header in need_headers:
        v = Header.objects.get(key=header).value
        req.add_header(header, v)

    res = request.urlopen(req)
    try:
        r = res.read().decode('utf-8')
        ret = json.loads(r)['status']
    except:
        ret = 0
    return ret


def wx_get_token():
    need_cookie_list = ['uuid', 'bizuin', 'ticket', 'ticket_id', 'account', 'cert', 'ticket_uin', 'login_certificate',
                        'ticket_certificate', 'fake_id', 'login_sid_ticket', 'noticeLoginFlag', 'ua_id']
    url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login&token=&lang=zh_CN'
    post_data = parse.urlencode({
        'token': '',
        'lang': 'zh_CN',
        'ajax': '1',
        'f': 'json',
        'random': str(random.random()),
    }).encode('utf-8')

    req = request.Request(url, post_data)

    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('Referer', 'https://mp.weixin.qq.com' + Setting.objects.get(key='redirect_url').value)
    req.add_header('Accept-Encoding', 'gzip, deflate, br')
    req.add_header('Cookie', get_cookie(need_cookie_list))
    res = request.urlopen(req)

    add_cookie_from_header(res.getheaders())
    try:
        content = res.read().decode('utf-8')
        print(content)
        ret = json.loads(content)['redirect_url']
        token = ret[ret.rindex('=') + 1:]
        Setting.create('token', token)
        return True
    except:
        return False
