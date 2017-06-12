from urllib import request

from bs4 import BeautifulSoup
from django.utils.crypto import get_random_string

from qiniu import Auth, put_file, etag


class CloudDN:
    ak = 'fhC4mquqyfhRtfWrdVXGBiLTuCcarfQRXYCH3TZc'
    sk = 'QGKEFMJJimYNKAzwGdvvC5goeuEoShG6PmWl69I-'
    host = 'http://zeus.chaping.io/'
    bucket_name = 'zeus'

    @staticmethod
    def get_auth():
        return Auth(access_key=CloudDN.ak, secret_key=CloudDN.sk)

    @staticmethod
    def upload_file(q, key, local_file):
        token = q.upload_token(CloudDN.bucket_name, key, 3600)
        print('Upload ', local_file)
        ret, info = put_file(up_token=token, key=key, file_path=local_file)
        assert ret['key'] == key
        assert ret['hash'] == etag(local_file)


def download_img(url, local_file):
    req = request.Request(url)
    res = request.urlopen(req, timeout=30)
    data = res.read()
    # print('Save as', local_file)
    with open(local_file, "wb") as f:
        f.write(data)


def deal_html(html, cover, timestamp):
    timestamp = str(timestamp)

    def has_attr_data_src(tag):
        return tag.has_attr('data-src')

    soup = BeautifulSoup(html, "html.parser")
    q = CloudDN.get_auth()
    for item in soup.find_all(has_attr_data_src):
        item['src'] = item['data-src']
        url = item['src']
        item['data-src'] = None
        if item.name == 'img':
            sub_key = timestamp + '_' + get_random_string(length=16)
            local_file = 'temp_images/' + sub_key
            key = 'img/' + sub_key
            try:
                # print("Download", url)
                download_img(url, local_file)
                CloudDN.upload_file(q, key, local_file)
            except:
                key = 'img/error'
            item['src'] = CloudDN.host + key

    sub_key = timestamp + '_' + get_random_string(length=16)
    local_file = 'temp_images/' + sub_key
    key = 'img/' + sub_key
    # print("Download", cover)
    try:
        download_img(cover, local_file)
        CloudDN.upload_file(q, key, local_file)
    except:
        key = 'img/error'

    return str(soup), CloudDN.host + key
