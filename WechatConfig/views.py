import json
import random
import re


from Article.models import Article, Comment, ArticleAnalyse, ArticleAnalyseShare
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
    Setting.create('username', 'Chaping321@163.com')
    Setting.create('pwd', 'afd0410fbec5081474db9d7e4a5bc5c8')
    return response()


def grab_article_content(url):
    try:
    #     print('start grab')
        content = abstract_grab(url)
        content = content[content.find('<div class="rich_media_content " id="js_content">'):]
        content = content[content.find('<p'):]
        content = content[:content.find('</div>')]
        return content[:-24]
    except:
        return None


def grab_article(count, begin):
    count = str(count)
    begin = str(begin)
    token = Setting.objects.get(key='token').value
    url = "https://mp.weixin.qq.com/cgi-bin/newmasssendpage?count=" + count + "&begin=" + begin + \
          "&token=" + token + "&lang=zh_CN&f=json&ajax=1&random=" + str(random.random())
    content = json.loads(abstract_grab(url))

    if content['base_resp']['ret'] != 0:
        return False

    for item in content['sent_list']:
        # print(item['sent_result'])
        if item['sent_result']['msg_status'] == 6:
            continue
        send_time = item['sent_info']['time']
        for index, article in enumerate(item['appmsg_info']):
            o_article = Article.create(index, article, send_time)
            article_update(o_article)
    return True


def article_update(o_article):
    dr = re.compile(r'<[^>]+>', re.S)

    if not o_article.is_delete:
        if o_article.status == Article.STEP_CREATE:
            o_article.content = grab_article_content(o_article.content_url)
            if o_article.content is not None:
                o_article.content_pure = dr.sub('', o_article.content)
                o_article.status = Article.STEP_CONTENT
        if o_article.status == Article.STEP_CONTENT:
            o_article.cdn_content, o_article.cdn_cover = \
                deal_html(o_article.content, o_article.cover, o_article.send_time)
            o_article.status = Article.STEP_QINIU
        if o_article.status == Article.STEP_QINIU:
            ret = grab_comment_pages(o_article.comment_id)
            if ret:
                o_article.status = Article.STEP_COMMENT
    o_article.save()


def grab_share_num():
    token = Setting.objects.get(key='token').value
    url = 'https://mp.weixin.qq.com/misc/appmsganalysis?action=all&order_direction=2&token=' + token + '&lang=zh_CN'
    content = abstract_grab(url)
    try:
        content = re.search('window.cgiData2 = (.*?);', content, flags=0).group(1)
        msgs = json.loads(content)['list']
    except:
        return False

    share_dict = {}
    for item in msgs:
        article_id = item['msgid']
        if article_id in share_dict:
            share_dict[article_id] += item['share_user']
        else:
            share_dict[article_id] = item['share_user']
    for article_id, share_num in share_dict.items():
        Article.set_share(article_id, share_num)
    return True


def grab_comment_by_comment_id(token, comment_id, count, begin):
    count = str(count)
    begin = str(begin)
    url = 'https://mp.weixin.qq.com/misc/appmsgcomment?action=list_comment&mp_version=7&type=1&comment_id=' + \
          comment_id + '&begin=' + begin + '&count=' + count + '&token=' + token + '&lang=zh_CN'
    content = abstract_grab(url)
    try:
        content = re.search('list : (.*?)\n', content, flags=0).group(1)
        content = content[:-1]
        comment_msg = json.loads(content)
    except:
        return -1
    for s_comment in comment_msg['comment']:
        Comment.create(comment_id, s_comment)
    return comment_msg['total_elected_count']


def grab_comment_pages(comment_id):
    token = Setting.objects.get(key='token').value
    count, begin = 10, 0
    total_num = grab_comment_by_comment_id(token, comment_id, count, begin)
    if total_num == -1:
        return False
    while total_num > count + begin:
        begin += count
        total_num = grab_comment_by_comment_id(token, comment_id, count, begin)
        if total_num == -1:
            return False
    return True


# def grab_comment(request):
#     for o_article in Article.objects.all():
#         article_update(o_article)
#     return response()
#
#

def get_packed_article(o_article):
    # o_article = Article.objects.get(pk=1)
    return dict(
        title=o_article.title,
        send_time=o_article.send_time,
        article_id=o_article.article_id,
        content_url=o_article.content_url,
        read_num=o_article.read_num,
        comment_num=o_article.comment_num,
        share_num=o_article.share_num,
        like_num=o_article.like_num,
    )


def get_article(request, date_time, count):
    """
    获取文章列表
    :param date_time: 起始时间戳
    :param count: 从起始时间回溯的条目
    """
    try:
        date_time = int(date_time)
        count = int(count)
        if count > 10:
            count = 10
        if count <= 0:
            count = 1
    except:
        return response(code=-1, msg='类型错误')
    articles = Article.objects.filter(send_time__lte=date_time).order_by('-send_time')
    filter_articles = []
    next_date_time = 0
    for o_article in articles:
        if o_article.send_time != next_date_time:
            next_date_time = o_article.send_time
            count -= 1
            if count < 0:
                break
        filter_articles.append(get_packed_article(o_article))
    return response(body=dict(articles=filter_articles, next_date_time=next_date_time))


def get_article_analyse(request, article_id):
    try:
        o_article = Article.objects.get(article_id=article_id)
    except:
        return response(code=1, msg='错误的文章ID')
    analyse_list = []
    analyses = ArticleAnalyse.objects.filter(article=o_article)
    for o_analyse in analyses:
        analyse_list.append(dict(
            like_num=o_analyse.like_num,
            comment_num=o_analyse.comment_num,
            read_num=o_analyse.read_num,
            reprint_num=o_analyse.reprint_num,
            create_time=int(o_analyse.create_time.timestamp()),
        ))
    analyse_list_share = []
    analyses = ArticleAnalyseShare.objects.filter(article=o_article)
    for o_analyse in analyses:
        analyse_list_share.append(dict(
            share_num=o_analyse.share_num,
            create_time=int(o_analyse.create_time.timestamp()),
        ))
    return response(body=dict(analyse=analyse_list, analyse_share=analyse_list_share))


def get_comment(request, article_id):
    try:
        o_article = Article.objects.get(article_id=article_id)
    except:
        return response(code=1, msg='错误的文章ID')
    comments = Comment.objects.filter(comment_id=o_article.comment_id)

    comment_list = []
    for comment in comments:
        comment_list.append(dict(
            nick_name=comment.nick_name,
            post_time=comment.post_time,
            content=comment.content,
            icon=comment.icon,
        ))
    return response(body=dict(comments=comment_list))


def grab_article_list(request):
    """
    抓取最新文章并更新更新分享量
    """
    ret = grab_article(7, 0)
    if not ret:
        return response(code=1, msg='抓取文章失败，请尝试重新登录')
    ret = grab_article(7, 7)
    if not ret:
        return response(code=1, msg='抓取文章失败，请尝试重新登录')
    ret = grab_share_num()
    if not ret:
        return response(code=2, msg='抓取最新分享数据失败')
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
        return response(body=1, msg='还没人扫')
    if wx_get_token():
        return response(body=0, msg='登录成功')
    else:
        return response(body=2, msg='登录失败')
