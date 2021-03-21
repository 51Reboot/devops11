from django.db import models

from base.model import BaseModel

from apps.user.models import UserProfile
# Create your models here.


class Publisher(BaseModel):
    """出版社"""
    name = models.CharField(max_length=32, unique=True, verbose_name='名称')
    address = models.CharField(max_length=100, verbose_name='地址')

    def __str__(self):
        return '{}: {}'.format(self.name, self.address)

    class Meta:
        verbose_name = '出版社'
        verbose_name_plural = verbose_name

    def serializer(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "address": self.address,
        }


class Book(BaseModel):
    """图书 ForeignKey 要放到多的一方"""
    PUBLISHER_CHOICE = (
        (1, '发行中'),
        (2, '已发行'),
    )

    name = models.CharField(max_length=32, verbose_name='书名')
    # 一对多 | 多对一
    publisher = models.ForeignKey(
        to=Publisher,
        default=28,
        on_delete=models.DO_NOTHING,
        verbose_name='出版社'
    )
    publisher_state = models.IntegerField(
        choices=PUBLISHER_CHOICE,
        verbose_name='出版社状态'
    )
    authors = models.ManyToManyField(
        to=UserProfile,
        null=True,
        blank=True,
        verbose_name='作者'
    )
    price = models.FloatField(default=69, verbose_name="价格")
    remark = models.TextField(
        verbose_name='评论'
    )

    def __str__(self):
        return "<object {}>".format(self.name)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = verbose_name