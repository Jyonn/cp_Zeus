"""cp_Zeus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, static

# from django.contrib import admin

from WechatConfig import views
from cp_Zeus.settings import STATIC_FILE

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    # url(r'^api/init$', views.init),

    url(r'^api/login/scan$', views.get_login_image_scan),
    url(r'^api/login/check-in$', views.check_login),

    url(r'^api/article/grab$', views.grab_article_list),

    url(r'^api/article/get/(?P<date_time>\d+)/(?P<count>\d+)$', views.get_article),
    url(r'^api/article/analyse/(?P<article_id>\w+)$', views.get_article_analyse),
    url(r'^api/article/comment/(?P<article_id>\w+)$', views.get_comment),
    # url(r'^api/article/comment', views.grab_comment),
    # url(r'^api/article/fixed$', views.fix_seq_article_id),
    # url(r'^api/article/all$', grab_history_article),
]

urlpatterns += static.static('/', document_root=STATIC_FILE)
