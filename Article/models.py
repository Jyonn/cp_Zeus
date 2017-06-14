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
    STEP_COMMENT = 3
    STEP_TABLE = (
        (STEP_CREATE, '创建条目'),
        (STEP_CONTENT, '抓取内容'),
        (STEP_QINIU, '转存七牛'),
        (STEP_COMMENT, '抓取评论'),
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

    @staticmethod
    def set_share(article_id, share_num):
        article_id = article_id[:-1] + str(int(article_id[-1]) - 1)
        try:
            o_article = Article.objects.get(article_id=article_id)
            o_article.share_num = share_num
            o_article.save()
        except:
            return

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


class Comment(models.Model):
    content_id = models.CharField(
        verbose_name='评论正文唯一ID',
        max_length=30,
        unique=True,
        db_index=True,
        default=None,
    )
    nick_name = models.CharField(
        verbose_name='用户昵称',
        max_length=100,
        default=None,
    )
    post_time = models.BigIntegerField(
        verbose_name='留言时间',
        default=0,
    )
    comment_id = models.CharField(
        verbose_name='文章评论ID',
        db_index=True,
        max_length=20,
        default=None,
    )
    content = models.CharField(
        verbose_name='评论正文',
        max_length=1023,
        default=None,
    )
    icon = models.CharField(
        verbose_name='评论头像',
        max_length=1200,
        default=None,
    )
    article_comment_id = models.IntegerField(
        verbose_name='文章评论序号',
        help_text='第几个评论的',
        default=0,
    )
    is_elected = models.IntegerField(
        verbose_name='是否被选择作为精选留言',
        default=0,
    )
    is_top = models.IntegerField(
        verbose_name='是否为置顶留言',
        default=0,
    )
    my_id = models.IntegerField(
        verbose_name='我还真不知道这个字段有啥卵用',
        default=0,
    )
    status = models.IntegerField(
        verbose_name='我还真不知道这个字段有啥卵用',
        default=0,
    )
    del_flag = models.IntegerField(
        verbose_name='应该是是否删除',
        default=0,
    )

    @classmethod
    def create(cls, comment_id, s_comment):
        o_comment = cls(
            content_id=s_comment['content_id'],
            nick_name=s_comment['nick_name'],
            post_time=s_comment['post_time'],
            comment_id=comment_id,
            content=s_comment['content'],
            icon=s_comment['icon'],
            article_comment_id=s_comment['id'],
            is_elected=s_comment['is_elected'],
            is_top=s_comment['is_top'],
            my_id=s_comment['my_id'],
            status=s_comment['status'],
            del_flag=s_comment['del_flag'],
        )
        try:
            o_comment.save()
        except:
            return
        for s_reply in s_comment['reply']['reply_list']:
            CommentReply.create(o_comment.content_id, s_reply)


class CommentReply(models.Model):
    content_reply_id = models.CharField(
        verbose_name='评论回复唯一ID',
        max_length=50,
        unique=True,
        db_index=True,
    )
    content_id = models.CharField(
        verbose_name='Comment表评论正文唯一ID',
        max_length=30,
        default=None,
    )
    reply_id = models.IntegerField(
        verbose_name='回复ID',
        default=0,
    )
    content = models.CharField(
        verbose_name='回复正文',
        max_length=1023,
        default=None,
    )
    create_time = models.BigIntegerField(
        verbose_name='回复时间',
        default=0,
    )
    reply_like_num = models.IntegerField(
        verbose_name='回复的点赞数',
        default=0,
    )
    to_uin = models.CharField(
        verbose_name='我还真不知道这个字段有啥卵用',
        max_length=20,
        default=None,
    )
    uin = models.CharField(
        verbose_name='我还真不知道这个字段有啥卵用',
        max_length=20,
        default=None,
    )

    @classmethod
    def create(cls, content_id, s_reply):
        content_reply_id = content_id + '_' + str(s_reply['reply_id'])
        o_reply = cls(
            content_reply_id=content_reply_id,
            content_id=content_id,
            content=s_reply['content'],
            create_time=s_reply['create_time'],
            reply_like_num=s_reply.get('reply_like_num', 0),
            to_uin=s_reply['to_uin'],
            uin=s_reply['uin'],
        )
        try:
            o_reply.save()
        finally:
            return
