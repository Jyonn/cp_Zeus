# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-12 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Article', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='cdn_content',
            field=models.TextField(default=None, null=True, verbose_name='转存到七牛云的文章正文'),
        ),
        migrations.AlterField(
            model_name='article',
            name='cdn_cover',
            field=models.CharField(default=None, max_length=1023, null=True, verbose_name='转存到七牛云的头图'),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(default=None, null=True, verbose_name='文章正文'),
        ),
        migrations.AlterField(
            model_name='article',
            name='content_pure',
            field=models.TextField(default=None, null=True, verbose_name='纯文字文章正文'),
        ),
    ]