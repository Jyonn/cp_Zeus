from django.db import models


class AbstractDict(models.Model):
    key = models.CharField(
        verbose_name='键',
        max_length=100,
        unique=True,
    )
    value = models.CharField(
        verbose_name='值',
        max_length=500,
    )

    class Meta:
        abstract = True


class Cookie(AbstractDict):
    @classmethod
    def create(cls, key, value):
        try:
            o_cookie = Cookie.objects.get(key=key)
            o_cookie.value = value
        except:
            o_cookie = cls(key=key, value=value)
        o_cookie.save()
        return o_cookie


class Header(AbstractDict):
    @classmethod
    def create(cls, key, value):
        try:
            o_header = Header.objects.get(key=key)
            o_header.value = value
        except:
            o_header = cls(key=key, value=value)
        o_header.save()
        return o_header


class Setting(AbstractDict):
    @classmethod
    def create(cls, key, value):
        try:
            o_setting = Setting.objects.get(key=key)
            o_setting.value = value
        except:
            o_setting = cls(key=key, value=value)
        o_setting.save()
        return o_setting
