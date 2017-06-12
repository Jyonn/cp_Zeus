from urllib import request

import zlib

from WechatConfig.login import get_cookie
from WechatConfig.models import Setting


def abstract_grab(url):
    token = Setting.objects.get(key='token').value

    req = request.Request(url)

    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    req.add_header("Accept-Encoding", "gzip")
    req.add_header("Accept-Language", "zh-CN,zh;q=0.8")
    req.add_header("Cache-Control", "max-age=0")
    req.add_header("Connection", "keep-alive")
    req.add_header("Cookie", get_cookie())
    req.add_header("Host", "mp.weixin.qq.com")
    req.add_header("Referer",
                   "https://mp.weixin.qq.com/cgi-bin/masssendpage?t=mass/send&token=" + token + "&lang=zh_CN")
    req.add_header("Upgrade-Insecure-Requests", "1")
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/56.0.2924.87 Safari/537.36")

    res = request.urlopen(req)
    gzipped = res.headers.get('Content-Encoding')
    compressed_data = res.read()
    res.close()
    if gzipped:
        content = zlib.decompress(compressed_data, 16+zlib.MAX_WBITS)
    else:
        content = compressed_data
    content = content.decode("utf-8")

    return content
