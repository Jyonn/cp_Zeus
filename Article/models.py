from django.db import models


class Article(models.Model):
    """
    文章类
    """
    L = {
        'appmsgid': 20,
        'comment_id': 20,
        'title': 511,
        'cover': 1023,
        'content_url': 1023,
        'sn': 40,
        'article_id': 30,
    }
    STEP_CREATE = 0
    STEP_CONTENT = 1
    STEP_QINIU = 2
    STEP_TABLE = (
        (STEP_CREATE, '创建条目'),
        (STEP_CONTENT, '抓取内容'),
        (STEP_QINIU, '转存七牛'),
    )
    appmsgid = models.CharField(
        verbose_name='推送消息ID',
        help_text='一条推送消息可以有多篇文章',
        max_length=L['appmsgid'],
        default=None,
    )
    seq = models.IntegerField(
        verbose_name='推送的第几条',
        default=0,
    )
    article_id = models.CharField(
        verbose_name='文章唯一ID',
        max_length=L['article_id'],
        primary_key=True,
    )
    comment_id = models.CharField(
        verbose_name='文章评论ID',
        max_length=L['comment_id'],
        default=None,
    )
    comment_num = models.IntegerField(
        verbose_name='评论数',
        default=0,
    )
    reprint_num = models.IntegerField(
        verbose_name='转载数',
        help_text='公众号转载，非转发数',
        default=0,
    )
    like_num = models.IntegerField(
        verbose_name='点赞数',
        default=0,
    )
    read_num = models.IntegerField(
        verbose_name='阅读量',
        default=0,
    )
    share_num = models.IntegerField(
        verbose_name='分享量',
        default=0,
    )
    title = models.CharField(
        verbose_name='标题',
        max_length=L['title'],
        default=None,
    )
    cover = models.CharField(
        verbose_name='头图',
        max_length=L['cover']
    )
    content_url = models.CharField(
        verbose_name='文章正文链接',
        max_length=L['content_url'],
    )
    # sn = models.CharField(
    #     verbose_name='文章链接参数',
    #     max_length=L['sn'],
    # )
    is_delete = models.BooleanField(
        verbose_name='是否删除',
        default=False,
    )
    send_time = models.BigIntegerField(
        verbose_name='推送时间',
        default=0,
    )

    content = models.TextField(
        verbose_name='文章正文',
        default=None,
        null=True,
    )
    content_pure = models.TextField(
        verbose_name='纯文字文章正文',
        default=None,
        null=True,
    )

    cdn_cover = models.CharField(
        verbose_name='转存到七牛云的头图',
        max_length=L['cover'],
        default=None,
        null=True,
    )
    cdn_content = models.TextField(
        verbose_name='转存到七牛云的文章正文',
        default=None,
        null=True,
    )
    status = models.IntegerField(
        verbose_name='文章抓取状态',
        choices=STEP_TABLE,
        default=STEP_CREATE,
    )

    @classmethod
    def create(cls, seq, article_dict, send_time):
        appmsgid = str(article_dict['appmsgid'])
        article_id = appmsgid + '_' + str(seq)
        content_url = article_dict['content_url'].replace('&amp;', '&')
        cover = article_dict['cover'].replace('&amp;', '&')

        try:
            o_article = Article.objects.get(article_id=article_id)
            o_article.comment_num = article_dict['comment_num']
            o_article.like_num = article_dict['like_num']
            o_article.read_num = article_dict['read_num']
            o_article.reprint_num = article_dict.get('reprint_num', 0)
            o_article.is_delete = article_dict['is_deleted']
        except models.ObjectDoesNotExist:
            o_article = cls(
                appmsgid=appmsgid,
                seq=seq,
                article_id=article_id,
                comment_id=article_dict['comment_id'],
                comment_num=article_dict['comment_num'],
                like_num=article_dict['like_num'],
                read_num=article_dict['read_num'],
                reprint_num=article_dict.get('reprint_num', 0),
                share_num=0,
                title=article_dict['title'],
                cover=cover,
                is_delete=article_dict['is_deleted'],
                content_url=content_url,
                send_time=send_time,
                status=Article.STEP_CREATE,
            )
        o_article.save()

        return o_article

# class ArticleAnalyse(models.Model):
#     article = models.ForeignKey(
#         Article,
#         verbose_name='关联文章'
#     )
#     create_time = models.DateTimeField(
#         verbose_name='创建时间',
#         auto_now=True,
#         auto_created=True,
#     )
#     comment_num = models.IntegerField(
#         verbose_name='评论数',
#         default=0,
#     )
#     reprint_num = models.IntegerField(
#         verbose_name='转载数',
#         help_text='公众号转载，非转发数',
#         default=0,
#     )
#     like_num = models.IntegerField(
#         verbose_name='点赞数',
#         default=0,
#     )
#     read_num = models.IntegerField(
#         verbose_name='阅读量',
#         default=0,
#     )
#     share_num = models.IntegerField(
#         verbose_name='分享量',
#         default=0,
#     )
