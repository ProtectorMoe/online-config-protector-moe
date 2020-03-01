from django.db import models
import time


class UserBase(models.Model):
    uid = models.IntegerField(verbose_name='uid')
    username = models.CharField(max_length=32, verbose_name='用户名')
    salt = models.CharField(max_length=32, verbose_name='salt')
    create_time = models.IntegerField(default=time.time, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'用户 {self.uid}-{self.username}'


class Path(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    author = models.TextField(max_length=32, default='匿名', verbose_name='作者')

    title = models.TextField(verbose_name='标题')
    desc = models.TextField(verbose_name='描述')
    user_like = models.ManyToManyField(UserBase, related_name='user_like')
    create_time = models.IntegerField(default=time.time, blank=True, verbose_name='创建时间')
    last_download = models.IntegerField(default=time.time, blank=True, verbose_name='最后下载时间')
    path_pc = models.TextField(default='{}', verbose_name='电脑版JSON')
    path_pe = models.TextField(default='{}', verbose_name='手机版JSON')

    class Meta:
        verbose_name = '配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'用户: {self.author}\n' \
               f'标题: {self.title}\n' \
               f'描述: {self.desc}\n' \
               f'时间: {self.create_time}\n'
