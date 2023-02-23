# *_*coding:utf-8 *_*
# @Author : Reggie
from django.db import models
from django.utils.html import format_html


# Create your models here.

class BaseTime(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class BaseMinioImage(models.Model):
    show_abs_url = models.BooleanField(default=False, verbose_name="show abs url")
    abs_host = models.CharField(max_length=200, verbose_name="abs host", blank=True, null=True)

    class Meta:
        abstract = True

    def image(self, img_attname):
        if not hasattr(self, img_attname):
            raise ValueError(f"has not attname: {img_attname}")
        image = getattr(self, img_attname)
        if not image:
            return ""
        url = image.url
        if self.show_abs_url:
            abs_host = image.storage.abs_host
            if self.abs_host:
                abs_host = self.abs_host
            secure = image.storage.secure
            if not abs_host.startswith("http"):
                abs_host = f"http{'s' if secure else ''}://{abs_host}"
            abs_host = abs_host.rstrip("/")
            abs_host = abs_host.rstrip("\\")
            url = url.lstrip("/")
            url = url.lstrip("\\")
            url = f"{abs_host}/{url}"
        result = format_html(
            '<img src="{}" width="156px" height="98px"/>',
            url,
        )
        return result
