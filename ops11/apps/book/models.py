from django.db import models

from base.model import BaseModel
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