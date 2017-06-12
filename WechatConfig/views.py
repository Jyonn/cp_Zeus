import json
import random
import re

from Article.models import Article
from WechatConfig.login import wx_login, wx_visit_page, wx_get_scan_image, wx_check_image_scanned, wx_get_token
from WechatConfig.models import Header, Setting
from base.clouddn import deal_html
from base.grab import abstract_grab
from base.response import response


def init(request):
    Header.create('Host', 'mp.weixin.qq.com')
    Header.create('Origin', 'https://mp.weixin.qq.com')
    Header.create('Connection', 'close')
    Header.create('X-Requested-With', 'XMLHttpRequest')
    Header.create('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/56.0.2924.87 Safari/537.36')
    Header.create('Accept-Encoding', 'gzip, deflate, br')
    Header.create('Accept-Language', 'zh-CN,zh;q=0.8')
    Header.create('Upgrade-Insecure-Requests', '1')
    Setting.create('token', '0')
    Setting.create('status', 'need-login')
    return response()


def grab_article_content(url):
    # try:
        print('start grab')
        content = abstract_grab(url)
        content = content[content.find('<div class="rich_media_content " id="js_content">'):]
        content = content[content.find('<p'):]
        content = content[:content.find('</div>')]
        return content[:-24]
    # except:
    #     return None


def grab_article(count, begin):
    token = Setting.objects.get(key='token').value
    url = "https://mp.weixin.qq.com/cgi-bin/newmasssendpage?count=" + count + "&begin=" + begin + \
          "&token=" + token + "&lang=zh_CN&f=json&ajax=1&random=" + str(random.random())
    content = json.loads(abstract_grab(url))

    if content['base_resp']['ret'] != 0:
        return False

    for item in content['sent_list']:
        send_time = item['sent_info']['time']
        for index, article in enumerate(item['appmsg_info']):
            o_article = Article.create(index, article, send_time)
            article_update(o_article)


def article_update(o_article):
    dr = re.compile(r'<[^>]+>', re.S)

    if not o_article.is_delete:
        if o_article.status == Article.STEP_CREATE:
            o_article.content = grab_article_content(o_article.content_url)
            print('none?', o_article.content is None)
            if o_article.content is not None:
                o_article.content_pure = dr.sub('', o_article.content)
                o_article.status = Article.STEP_CONTENT
        if o_article.status == Article.STEP_CONTENT:
            o_article.cdn_content, o_article.cdn_cover = \
                deal_html(o_article.content, o_article.cover, o_article.send_time)
            o_article.status = Article.STEP_QINIU
    o_article.save()


def grab_article_list(request):
    grab_article(7, 0)
    return response()


def grab_history_article(request):
    for index in range(724):
        grab_article(7, index)
    return response()


def get_login_image_scan(request):
    wx_login()
    wx_visit_page()
    image_path = wx_get_scan_image()
    return response(body=image_path)


def check_login(request):
    ret = wx_check_image_scanned()
    if ret == 0:
        return response(body=-1, msg='还没人扫')
    if wx_get_token():
        return response(body=0, msg='登录成功')
    else:
        return response(body=1, msg='登录失败')
